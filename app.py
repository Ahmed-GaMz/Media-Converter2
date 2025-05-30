from flask import Flask, render_template, request, send_file
from PIL import Image
import os
import moviepy.editor as mp
import uuid

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_image(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['jpg', 'jpeg', 'png', 'webp']

def allowed_video(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['mp4', 'mov', 'avi', 'mkv', 'webm']

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert/<mode>', methods=['POST'])
def convert(mode):
    file = request.files.get('file')
    if not file:
        return 'No file uploaded', 400

    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)

    if mode == 'custom':
        output_format = request.form.get('format')
        width = int(request.form.get('width')) if request.form.get('width') else None
        height = int(request.form.get('height')) if request.form.get('height') else None

        if allowed_image(file.filename):
            im = Image.open(filepath)
            if width and height:
                im = im.resize((width, height))
            output_path = os.path.join(UPLOAD_FOLDER, f"converted.{output_format}")
            im.save(output_path, format=output_format.upper())
        
        elif allowed_video(file.filename):
            clip = mp.VideoFileClip(filepath)
            output_path = os.path.join(UPLOAD_FOLDER, f"converted.{output_format}")
            clip.write_videofile(output_path, codec='libx264')
        
        else:
            return 'Unsupported file type for custom', 400

    elif mode == 'telegram':
        if allowed_image(file.filename):
            im = Image.open(filepath).convert("RGBA")
            im.thumbnail((512, 512))  # Resize to fit within 512x512
            output_path = os.path.join(UPLOAD_FOLDER, 'telegram_image.webp')
            im.save(output_path, format='WEBP', quality=80, method=6)
        
        elif allowed_video(file.filename):
            clip = mp.VideoFileClip(filepath)
            subclip = clip.subclip(0, min(3, clip.duration))
            if clip.h > 512:
                subclip = subclip.resize(height=512)
            output_path = os.path.join(UPLOAD_FOLDER, 'telegram_video.webm')
            subclip.write_videofile(output_path, codec='libvpx', audio=False)
        
        else:
            return 'Unsupported file type for telegram', 400

    else:
        return 'Invalid conversion mode', 400

    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)