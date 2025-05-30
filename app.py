
from flask import Flask, request, render_template, send_file
import os
from PIL import Image
import subprocess

app = Flask(__name__)
UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert-image', methods=['POST'])
def convert_image():
    file = request.files['file']
    format = request.form['format']
    output_path = os.path.join(UPLOAD_FOLDER, f"converted.{format.lower()}")

    image = Image.open(file)
    image.save(output_path, format.upper())
    return send_file(output_path, as_attachment=True)

@app.route('/convert-video', methods=['POST'])
def convert_video():
    file = request.files['file']
    format = request.form['format']
    input_path = os.path.join(UPLOAD_FOLDER, file.filename)
    output_path = os.path.join(UPLOAD_FOLDER, f"converted.{format}")

    file.save(input_path)
    subprocess.run(['ffmpeg', '-i', input_path, output_path])
    return send_file(output_path, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
