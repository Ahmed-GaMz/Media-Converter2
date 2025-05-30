from flask import Flask, render_template, request, send_file
from PIL import Image
from moviepy.editor import VideoFileClip
import os
from io import BytesIO

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert():
    file = request.files["file"]
    output_format = request.form.get("output_format")
    width = request.form.get("width", type=int)
    height = request.form.get("height", type=int)

    filename = file.filename
    name, ext = os.path.splitext(filename)
    ext = ext.lower()

    output = BytesIO()

    if ext in [".jpg", ".jpeg", ".png", ".webp"]:
        image = Image.open(file)
        if width and height:
            image = image.resize((width, height))
        image.save(output, format=output_format.upper())
        output.seek(0)
        return send_file(output, mimetype=f"image/{output_format}", as_attachment=True, download_name=f"{name}.{output_format}")

    elif ext in [".mp4", ".mov", ".avi"]:
        clip = VideoFileClip(file.filename)
        clip.write_videofile(f"/tmp/{name}.{output_format}")
        return send_file(f"/tmp/{name}.{output_format}", as_attachment=True)

    else:
        return "Unsupported file type", 400

@app.route("/telegram_convert", methods=["POST"])
def telegram_convert():
    file = request.files["file"]
    filename = file.filename
    name, ext = os.path.splitext(filename)
    ext = ext.lower()

    output = BytesIO()

    if ext in [".jpg", ".jpeg", ".png"]:
        image = Image.open(file)
        image.thumbnail((512, 512))
        image.save(output, format="WEBP")
        output.seek(0)
        return send_file(output, mimetype="image/webp", as_attachment=True, download_name=f"{name}.webp")

    elif ext in [".mp4", ".mov", ".avi"]:
        path = f"/tmp/{name}"
        input_path = f"{path}{ext}"
        output_path = f"{path}_tg.webm"
        file.save(input_path)

        clip = VideoFileClip(input_path).subclip(0, 3)
        clip.write_videofile(output_path, codec="libvpx", audio_codec="libvorbis", fps=24)
        return send_file(output_path, as_attachment=True)

    else:
        return "Unsupported file type for Telegram", 400

if __name__ == "__main__":
    app.run(debug=True)