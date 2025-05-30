from flask import Flask, request, send_file, render_template
from PIL import Image
import moviepy.editor as mp
import os
import tempfile
import uuid

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert_image', methods=['POST'])
def convert_image():
    img = request.files['image']
    target_format = request.form['format'].lower()
    width = request.form.get('width', type=int)
    height = request.form.get('height', type=int)

    with tempfile.NamedTemporaryFile(delete=False, suffix='.' + target_format) as tmp:
        image = Image.open(img)

        if width and height:
            image = image.resize((width, height))

        if target_format == 'jpg':
            target_format = 'JPEG'
        else:
            target_format = target_format.upper()

        image.save(tmp.name, target_format)
        tmp_path = tmp.name

    return send_file(tmp_path, as_attachment=True, download_name=f"converted.{target_format.lower()}")

@app.route("/convert_tg_image", methods=["POST"])
def convert_tg_image():
    file = request.files["image"]
    if not file:
        return "لم يتم تحميل صورة"
    img = Image.open(file.stream).convert("RGBA")
    img.thumbnail((512, 512))
    filename = f"{uuid.uuid4()}.webp"
    path = os.path.join(UPLOAD_FOLDER, filename)
    img.save(path, "WEBP")
    return send_file(path, as_attachment=True)

@app.route("/convert_tg_video", methods=["POST"])
def convert_tg_video():
    file = request.files["video"]
    if not file:
        return "لم يتم تحميل فيديو"
    input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.mp4")
    output_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.webm")
    file.save(input_path)

    clip = mp.VideoFileClip(input_path)
    duration = min(3, clip.duration)
    clip = clip.subclip(0, duration)
    clip_resized = clip.resize(height=512 if clip.h > clip.w else None, width=512 if clip.w > clip.h else None)
    clip_resized.write_videofile(output_path, codec="libvpx", audio=False, verbose=False, logger=None)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)