# utils/downloader.py

import yt_dlp
import os
import uuid

def download_video(url, format_code):
    temp_id = str(uuid.uuid4())
    output_path = f"downloads/{temp_id}.%(ext)s"
    
    ydl_opts = {
        'outtmpl': output_path,
        'format': format_code,
        'quiet': True,
    }
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
    
    return filename, info.get("title", "Downloaded")

def get_formats(url):
    with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = []
        for fmt in info['formats']:
            if fmt.get('ext') in ['mp4', 'm4a'] and fmt.get('filesize'):
                formats.append({
                    'format_id': fmt['format_id'],
                    'ext': fmt['ext'],
                    'resolution': fmt.get('format_note') or fmt.get('height', ''),
                })
    return formats
  
