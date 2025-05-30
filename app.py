import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from moviepy.editor import VideoFileClip
from PIL import Image
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
CONVERTED_FOLDER = 'converted'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(CONVERTED_FOLDER, exist_ok=True)

# ---------- [ صفحة الموقع الرئيسية ] ----------
@app.route('/')
def index():
    return render_template('index.html')

# ---------- [ تحويل الملفات - كوستم ] ----------
@app.route('/convert', methods=['POST'])
def convert_file():
    file = request.files['file']
    output_format = request.form['format']
    width = int(request.form['width'])
    height = int(request.form['height'])

    if file:
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)

        # تحويل الفيديو
        if output_format in ['mp4', 'webm']:
            clip = VideoFileClip(input_path)
            clip_resized = clip.resize(newsize=(width, height))
            output_filename = f"{uuid.uuid4()}.{output_format}"
            output_path = os.path.join(CONVERTED_FOLDER, output_filename)
            clip_resized.write_videofile(output_path, codec='libx264' if output_format == 'mp4' else 'libvpx')
            return send_file(output_path, as_attachment=True)

        # تحويل الصور
        else:
            img = Image.open(input_path)
            img = img.resize((width, height))
            output_filename = f"{uuid.uuid4()}.{output_format}"
            output_path = os.path.join(CONVERTED_FOLDER, output_filename)
            img.save(output_path)
            return send_file(output_path, as_attachment=True)

    return "No file uploaded", 400

# ---------- [ تحويل ملفات خاصة بتليغرام ] ----------
@app.route('/telegram', methods=['POST'])
def telegram_convert():
    file = request.files['file']
    filetype = request.form['type']  # "image" or "video"

    if file:
        filename = secure_filename(file.filename)
        input_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(input_path)

        output_filename = f"{uuid.uuid4()}"
        if filetype == 'image':
            output_path = os.path.join(CONVERTED_FOLDER, output_filename + ".webp")
            with Image.open(input_path) as img:
                img = img.convert("RGBA")
                img.thumbnail((512, 512))
                img.save(output_path, "WEBP", lossless=True)
            return send_file(output_path, as_attachment=True)

        elif filetype == 'video':
            output_path = os.path.join(CONVERTED_FOLDER, output_filename + ".webm")
            clip = VideoFileClip(input_path).subclip(0, 3)
            clip_resized = clip.resize(height=512)
            clip_resized.write_videofile(output_path, codec='libvpx', audio=False)
            return send_file(output_path, as_attachment=True)

    return "No file uploaded", 400

# ---------- [ تشغيل التطبيق ] ----------
if __name__ == '__main__':
    app.run(debug=True)