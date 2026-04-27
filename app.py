import os
from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import yt_dlp
import imageio_ffmpeg

app = Flask(__name__)
CORS(app)

# Esse comando busca o executável do FFmpeg que a biblioteca baixou para nós
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "status": "Online",
        "mensagem": "Sua API de Download do YouTube está rodando perfeitamente!"
    })

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    start_time = request.args.get('start', '0')
    end_time = request.args.get('end', '')
    format_type = request.args.get('format', 'mp4')

    if not video_url:
        return jsonify({"error": "Nenhuma URL fornecida"}), 400

    out_tmpl = 'output.%(ext)s'
    download_sections = f"*{start_time}-{end_time}" if end_time else f"*{start_time}-inf"

    # Regra de formato blindada: Tenta juntar separado, se falhar pega o melhor arquivo único
    if format_type == 'mp4':
        format_selector = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
    else:
        format_selector = 'bestaudio/best'

    ydl_opts = {
        'format': format_selector,
        'outtmpl': out_tmpl,
        'force_overwrites': True,
        'cookiefile': 'cookies.txt',
        'ffmpeg_location': ffmpeg_path, # Aponta o motor de colagem para o yt-dlp
        'extractor_args': {
            # Permite que ele tente a web mobile, o app e o site normal até conseguir os arquivos
            'youtube': ['player_client=mweb,android,web']
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
        filename = f"output.{file_ext}"
        
        # Procura o arquivo caso o formato final fuja do padrão
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
