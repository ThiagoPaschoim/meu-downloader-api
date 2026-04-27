import os
import subprocess
import uuid
from flask import Flask, request, send_file, jsonify, after_this_request
from flask_cors import CORS
import imageio_ffmpeg

app = Flask(__name__)
# Permite que sites de fora (seu GitHub Pages) enviem arquivos para cá
CORS(app, resources={r"/*": {"origins": "*"}})

ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

@app.route('/', methods=['GET'])
def index():
    return jsonify({"status": "Online", "mensagem": "Motor de Corte FFmpeg Ativo!"})

@app.route('/cut', methods=['POST'])
def cut_media():
    if 'file' not in request.files:
        return jsonify({"error": "Nenhum arquivo enviado"}), 400
    
    file = request.files['file']
    start_time = request.form.get('start', '00:00:00')
    end_time = request.form.get('end', '')

    if file.filename == '':
        return jsonify({"error": "Nenhum arquivo selecionado"}), 400

    # Cria nomes únicos para os arquivos (evita conflito se usar duas vezes seguidas)
    temp_id = str(uuid.uuid4())
    _, ext = os.path.splitext(file.filename)
    input_path = f"input_{temp_id}{ext}"
    output_path = f"output_{temp_id}{ext}"

    # Salva o arquivo temporariamente no servidor
    file.save(input_path)

    # Monta o comando de corte
    command = [ffmpeg_path, '-y', '-i', input_path, '-ss', start_time]
    if end_time:
        command.extend(['-to', end_time])
    # O comando "-c copy" corta o vídeo instantaneamente sem re-renderizar, mantendo a qualidade original
    command.extend(['-c', 'copy', output_path])

    try:
        # Executa o corte
        subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Agenda a limpeza do servidor para não lotar o disco gratuito do Render
        @after_this_request
        def remove_files(response):
            try:
                if os.path.exists(input_path): os.remove(input_path)
                if os.path.exists(output_path): os.remove(output_path)
            except Exception:
                pass
            return response
            
        return send_file(output_path, as_attachment=True, download_name=f"cortado_{file.filename}")
        
    except Exception as e:
        if os.path.exists(input_path): os.remove(input_path)
        return jsonify({"error": "Erro interno ao cortar o arquivo."}), 500

if __name__ == '__main__':
    app.run(debug=True)
