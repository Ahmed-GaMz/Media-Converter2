from flask import Flask, request, send_file, render_template
from PIL import Image
import os
import tempfile
import uuid
import moviepy.editor as mp

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

# تحويل الصور مع اختيار الصيغة والابعاد (Custom)
@app.route('/convert_image', methods=['POST'])
def convert_image():
    img = request.files.get('image')
    if not img:
        return "لم يتم رفع صورة", 400

    target_format = request.form.get('format', '').lower()
    width = request.form.get('width', type=int)
    height = request.form.get('height', type=int)

    if target_format not in ['png', 'jpeg', 'jpg', 'webp']:
        return "صيغة غير مدعومة", 400

    image = Image.open(img)
    if width and height:
        image = image.resize((width, height))

    if target_format == 'jpg':
        target_format = 'JPEG'
    else:
        target_format = target_format.upper()

    with tempfile.NamedTemporaryFile(delete=False, suffix='.' + target_format.lower()) as tmp:
        image.save(tmp.name, target_format)
        tmp_path = tmp.name

    return send_file(tmp_path, as_attachment=True, download_name=f"converted.{target_format.lower()}")

# تحويل صورة تلقائياً لتناسب ستكرات تلغرام (webp 512x512)
@app.route('/convert_tg_image', methods=['POST'])
def convert_tg_image():
    file = request.files.get('image')
    if not file:
        return "لم يتم رفع صورة", 400
    img = Image.open(file.stream).convert("RGBA")
    img.thumbnail((512, 512))
    filename = f"{uuid.uuid4()}.webp"
    path = os.path.join(UPLOAD_FOLDER, filename)
    img.save(path, "WEBP")
    return send_file(path, as_attachment=True)

# تحويل فيديو لتناسب فيديوهات تلغرام (webm أو mp4, 3 ثواني، أبعاد مناسبة)
@app.route('/convert_tg_video', methods=['POST'])
def convert_tg_video():
    file = request.files.get('video')
    if not file:
        return "لم يتم رفع فيديو", 400

    input_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.mp4")
    output_path = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}.webm")
    file.save(input_path)

    clip = mp.VideoFileClip(input_path)
    duration = min(3, clip.duration)
    clip = clip.subclip(0, duration)
    if clip.h > clip.w:
        clip_resized = clip.resize(height=512)
    else:
        clip_resized = clip.resize(width=512)

    clip_resized.write_videofile(output_path, codec="libvpx", audio=False, verbose=False, logger=None)

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run()