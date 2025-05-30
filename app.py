from flask import Flask, request, send_file, jsonify, render_template
from moviepy.editor import VideoFileClip
from PIL import Image
import io

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/convert', methods=['POST'])
def convert():
    try:
        file = request.files['file']
        target_format = request.form.get('format', '').lower()

        # إذا الملف صورة
        if file.content_type.startswith('image'):
            img = Image.open(file.stream)
            output = io.BytesIO()
            # الصيغ المدعومة للصور: webp, png, jpg/jpeg
            if target_format not in ['webp', 'png', 'jpg', 'jpeg']:
                return jsonify({'error': 'Unsupported image format'}), 400
            save_format = 'JPEG' if target_format in ['jpg', 'jpeg'] else target_format.upper()
            img.save(output, format=save_format)
            output.seek(0)
            return send_file(output, mimetype=f'image/{target_format}')

        # إذا الملف فيديو (للتلغرام فقط - اقص الفيديو إذا أكثر من 3 ثواني)
        elif file.content_type.startswith('video'):
            video = VideoFileClip(file.stream)

            # إذا في فورم خاص بالتلغرام، يعني شرط القص لازم ينطبق
            # حسب طلبك القسم الخاص بالتلغرام فقط يقص الفيديو لأقل من 3 ثواني
            # في حال كانت الصفحة تبعت التلغرام هي نفسها اللي ترسل الطلب، يمكن ترسل حقل extra مثلا
            # لكن هنا نفترض أنه دايركت الفيديو هو قسم التلغرام (أو ممكن تفصل endpoint)
            # الآن ببساطة اقص الفيديو لو أكثر من 3 ثواني
            if video.duration > 3:
                video = video.subclip(0, 3)

            output = io.BytesIO()
            # سنستخدم صيغة mp4 لأنها الأكثر توافقاً
            temp_filename = "temp_output.mp4"
            video.write_videofile(temp_filename, codec='libx264', audio_codec='aac', verbose=False, logger=None)
            with open(temp_filename, "rb") as f:
                output.write(f.read())
            output.seek(0)
            os.remove(temp_filename)

            return send_file(output, mimetype='video/mp4')

        else:
            return jsonify({'error': 'Unsupported file type'}), 400

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=10000)