import os
from flask import Flask, request, send_file
from flask_cors import CORS
import yt_dlp

app = Flask(__name__)
CORS(app) # Permite que seu site no GitHub Pages acesse esta API

@app.route('/download', methods=['GET'])
def download():
    video_url = request.args.get('url')
    start_time = request.args.get('start', '0') # Ex: "00:00:10"
    end_time = request.args.get('end', '0')     # Ex: "00:00:20"
    format_type = request.args.get('format', 'mp4')

    # Nome do arquivo temporário
    out_tmpl = 'downloaded_video.%(ext)s'
    
    # Configurações do yt-dlp para baixar apenas o trecho (Trimming)
# Configurações do yt-dlp para baixar apenas o trecho (Trimming)
# Configurações do yt-dlp para baixar apenas o trecho (Trimming)
# Configurações do yt-dlp para baixar apenas o trecho (Trimming)
# Configurações do yt-dlp para baixar apenas o trecho (Trimming)
    ydl_opts = {
        # Modificado: Pede o melhor formato combinado (b) para MP4, ou o melhor áudio (ba) para MP3
        'format': 'b[ext=mp4]/best' if format_type == 'mp4' else 'ba/bestaudio/best',
        'outtmpl': 'output',
        'force_overwrites': True,
        'download_sections': f"*{start_time}-{end_time}",
        'cookiefile': 'cookies.txt',
        'extractor_args': {
            'youtube': ['player_client=android']
        },
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
        
        return send_file(filename, as_attachment=True)
    except Exception as e:
        return {"error": str(e)}, 500

if __name__ == '__main__':
    app.run(debug=True)
