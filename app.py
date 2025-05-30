from flask import Flask, render_template, request, send_file
import os
import tempfile
from PIL import Image
import moviepy.editor as mp

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/convert", methods=["POST"])
def convert():
    file = request.files.get("file")
    convert_type = request.form.get("convert_type")

    if not file:
        return "No file uploaded.", 400

    if convert_type == "image":
        output_format = request.form.get("image_format")
        width = request.form.get("width")
        height = request.form.get("height")

        img = Image.open(file)
        if width and height:
            img = img.resize((int(width), int(height)))

        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_format}")
        img.save(output_file.name)
        return send_file(output_file.name, as_attachment=True)

    elif convert_type == "video":
        output_format = request.form.get("video_format")

        video = mp.VideoFileClip(file.stream)
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix=f".{output_format}")
        video.write_videofile(output_file.name, codec="libx264")
        return send_file(output_file.name, as_attachment=True)

    else:
        return "Unsupported conversion type", 400

if __name__ == "__main__":
    app.run(debug=True)