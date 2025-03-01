from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import tempfile

app = Flask(__name__)

def download_audio(url):
    try:
        # Create a temporary directory for the download
        temp_dir = tempfile.mkdtemp()
        output_path = os.path.join(temp_dir, "%(title)s.%(ext)s")

        # yt-dlp options
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': output_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            audio_file = filename.replace(".webm", ".mp3").replace(".m4a", ".mp3")

        return audio_file

    except Exception as e:
        return str(e)

@app.route('/download', methods=['POST'])
def download():
    try:
        data = request.json
        url = data.get("url")

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        audio_path = download_audio(url)

        if not os.path.exists(audio_path):
            return jsonify({"error": "Failed to download audio"}), 500

        return send_file(audio_path, as_attachment=True, mimetype="audio/mpeg")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
