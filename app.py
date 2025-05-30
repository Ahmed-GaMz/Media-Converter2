from flask import Flask, request, send_file, render_template
from PIL import Image
import os
import tempfile

app = Flask(__name__)

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

        # صيغة JPEG تحتاج اسم خاص
        if target_format == 'jpg':
            target_format = 'JPEG'
        else:
            target_format = target_format.upper()

        image.save(tmp.name, target_format)
        tmp_path = tmp.name

    return send_file(tmp_path, as_attachment=True, download_name=f"converted.{target_format.lower()}")

if __name__ == '__main__':
    app.run(debug=True)