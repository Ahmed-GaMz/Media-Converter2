from flask import Flask, request, send_file, jsonify, render_template
from moviepy.editor import VideoFileClip
from PIL import Image
import io
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert/custom', methods=['POST'])
def convert_custom():
    try:
        file = request.files['file']
        target_format = request.form.get('format', '').lower()
        width = request.form.get('width')
        height = request.form.get('height')

        if file.content_type.startswith('image'):
            img = Image.open(file.stream)
            # تعديل أبعاد الصورة لو محددة
            if width and height:
                try:
                    width = int(width)
                    height = int(height)
                    img = img.resize((width, height), Image.ANTIALIAS)
                except Exception:
                    pass

            output = io.BytesIO()
            if target_format not in ['webp', 'png', 'jpg', 'jpeg']:
                return jsonify({'error': 'Unsupported image format'}), 400

            save_format = 'JPEG' if target_format in ['jpg', 'jpeg'] else target_format.upper()
            img.save(output, format=save_format)
            output.seek(0)
            return send_file(output, mimetype=f'image/{target_format}')

        else:
            return jsonify({'error': 'Only image files supported in Custom section'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/convert/telegram', methods=['POST'])
def convert_telegram():
    try:
        file = request.files['file']

        if file.content_type.startswith('image'):
            img = Image.open(file.stream)
            # تحويل الصورة إلى webp بحجم 512x512 أو أقل مع الحفاظ على النسبة
            max_size = (512, 512)
            img.thumbnail(max_size, Image.ANTIALIAS)

            output = io.BytesIO()
            img.save(output, format='WEBP')
            output.seek(0)
            return send_file(output, mimetype='image/webp')

        elif file.content_type.startswith('video'):
            video = VideoFileClip(file.stream)
            # اقتطاع الفيديو إلى 3 ثواني فقط لو الفيديو أطول
            if video.duration > 3:
                video = video.subclip(0, 3)

            output = io.BytesIO()
            temp_filename = "temp_output.mp4"
            video.write_videofile(temp_filename, codec='libx264', audio_codec='aac', verbose=False, logger=None)
            with open(temp_filename, "rb") as f:
                output.write(f.read())
            output.seek(0)
            os.remove(temp_filename)

            return send_file(output, mimetype='video/mp4')

        else:
            return jsonify({'error': 'Unsupported file type in Telegram section'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, port=10000)