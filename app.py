import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app)

# --- Rota Raiz (Acaba com o Erro 404) ---
@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "Online",
        "mensagem": "Sua API de Download do YouTube está rodando perfeitamente!"
    })

# --- Rota de Download ---
@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    start_time = request.args.get('start', '0')
    end_time = request.args.get('end', '')
    format_type = request.args.get('format', 'mp4')

    if not video_url:
        return jsonify({"error": "Nenhuma URL fornecida"}), 400

    out_tmpl = 'output.%(ext)s'
    
    # Se o usuário não definiu tempo final, não usamos o parâmetro de corte
    download_sections = f"*{start_time}-{end_time}" if end_time else f"*{start_time}-inf"

    # Configurações otimizadas para o Cliente Android
    ydl_opts = {
        # 'best' pega o melhor arquivo já combinado (video+audio) que o Android permite
        'format': 'best' if format_type == 'mp4' else 'bestaudio/best',
        'outtmpl': out_tmpl,
        'force_overwrites': True,
        'cookiefile': 'cookies.txt',
        'extractor_args': {
            'youtube': ['player_client=android']
        },
        'download_sections': download_sections,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
        }] if format_type == 'mp3' else []
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        
        file_ext = 'mp3' if format_type == 'mp3' else 'mp4'
        # O yt-dlp pode salvar como .webm dependendo do que for o 'best', então buscamos o arquivo gerado
        filename = f"output.{file_ext}"
        
        # Fallback caso o yt-dlp baixe em um formato diferente (como webm ou mkv)
        if not os.path.exists(filename):
            for ext in ['webm', 'mkv', 'm4a']:
                if os.path.exists(f"output.{ext}"):
                    filename = f"output.{ext}"
                    break

        return send_file(filename, as_attachment=True)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
