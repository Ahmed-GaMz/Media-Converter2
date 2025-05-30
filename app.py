from flask import Flask, request, render_template, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
from moviepy.editor import VideoFileClip
import os
import uuid
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["PROCESSED_FOLDER"] = PROCESSED_FOLDER

# إنشاء المجلدات إذا غير موجودة
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)

@app.route("/")
def index():
    return render_template("index.html")

# ============= قسم كوستم =============
@app.route("/convert", methods=["POST"])
def convert():
    file = request.files.get("file")
    if not file:
        return "لم يتم رفع أي ملف", 400

    output_format = request.form.get("format")
    width = request.form.get("width")
    height = request.form.get("height")

    if not output_format:
        return "الرجاء اختيار صيغة التحويل", 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(input_path)

    name, ext = os.path.splitext(filename)
    output_filename = f"{uuid.uuid4()}.{output_format}"
    output_path = os.path.join(app.config["PROCESSED_FOLDER"], output_filename)

    try:
        if ext.lower() in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]:
            img = Image.open(input_path)
            if width and height:
                img = img.resize((int(width), int(height)))
            img.save(output_path, output_format.upper())
        elif ext.lower() in [".mp4", ".mov", ".avi", ".mkv"]:
            clip = VideoFileClip(input_path)
            if width and height:
                clip = clip.resize((int(width), int(height)))
            clip.write_videofile(output_path, codec='libx264')
        else:
            return "صيغة الملف غير مدعومة", 400

        return send_file(output_path, as_attachment=True)

    except Exception as e:
        return f"حدث خطأ أثناء التحويل: {str(e)}", 500


# ============= قسم تلغرام =============
@app.route("/telegram", methods=["POST"])
def telegram():
    file = request.files.get("file")
    if not file:
        return "يرجى رفع ملف", 400

    filename = secure_filename(file.filename)
    input_path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    file.save(input_path)

    name, ext = os.path.splitext(filename)

    try:
        # معالجة الصور
        if ext.lower() in [".jpg", ".jpeg", ".png", ".bmp"]:
            img = Image.open(input_path)
            img.thumbnail((512, 512))
            output_filename = f"{uuid.uuid4()}.webp"
            output_path = os.path.join(app.config["PROCESSED_FOLDER"], output_filename)
            img.save(output_path, "WEBP")
            return send_file(output_path, as_attachment=True)

        # معالجة الفيديو
        elif ext.lower() in [".mp4", ".mov", ".avi", ".mkv", ".webm"]:
            clip = VideoFileClip(input_path)

            # قص الفيديو إلى 3 ثواني
            duration = min(clip.duration, 3)
            trimmed = clip.subclip(0, duration)

            # تصغير الأبعاد إذا كانت كبيرة (تقديرياً مناسب لتلغرام)
            trimmed = trimmed.resize(height=512)

            output_filename = f"{uuid.uuid4()}.mp4"
            output_path = os.path.join(app.config["PROCESSED_FOLDER"], output_filename)

            trimmed.write_videofile(output_path, codec='libx264', audio_codec='aac')
            return send_file(output_path, as_attachment=True)

        else:
            return "صيغة الملف غير مدعومة في قسم التلغرام", 400

    except Exception as e:
        return f"حدث خطأ أثناء التحويل: {str(e)}", 500


if __name__ == "__main__":
    app.run(debug=True)