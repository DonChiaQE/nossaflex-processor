import os
from flask import Flask, flash, request, redirect, url_for, render_template, send_file
from werkzeug.utils import secure_filename
import zipfile
import tarfile
from random import randint
from exif import Image
import shutil

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'zip', 'tgz', 'gz', '.7z'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.secret_key = "super secret key"

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            print('herererereadqwe')
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        noss = request.form.get('noss')
        iso = request.form.get('iso')
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(UPLOAD_FOLDER, filename))
            zip_ref = zipfile.ZipFile(os.path.join(UPLOAD_FOLDER, filename), 'r')
            
            name = UPLOAD_FOLDER+f"/{filename.strip('.zip')}"

            zip_ref.extractall(UPLOAD_FOLDER+f"/{filename.strip('.zip')}")
            zip_ref.close()
            files = os.listdir(name)

            photos = []
            print(name)
            for f in files:
                if f.lower().endswith(('.png', '.jpg', '.jpeg', '.tiff', '.bmp')):
                    photos.append(f)
            
            print(photos)
            noss = noss.replace('\r', '')
            roll = noss.split('\n')
            print(roll)

            photos = list(reversed(sorted(photos, key=lambda x: int(os.path.splitext(x)[0]))))
            try: 
                if len(roll) == len(photos):
                    for index, shot in enumerate(roll):
                        with open(f'{name}/{photos[index]}', "rb") as f:
                            f_image = Image(f)
                        
                        print(shot)
                        print(index)
                        exif = shot.split('_')
                        print('exif', exif)
                        
                        f_image.focal_length = exif[4].strip('FL')
                        
                        f_image.exposure_bias_value = exif[5].strip('EX')
                        
                        f_image.f_number = exif[3].strip('A')
                        
                        if 's' in exif[2].strip("SS"):
                            exif = exif[2].strip("SS")
                            f_image.exposure_time = f'{exif.strip("s")}'
                        elif 'm' in exif[2].strip("SS"):
                            exif = exif[2].strip("SS")
                            exposure_time = int(exif.strip('m')) * 60
                            f_image.exposure_time = f'{exposure_time}'
                        elif 'h' in exif[2].strip("SS"):
                            exif = exif[2].strip("SS")
                            exposure_time = int(exif.strip('h')) * 60 * 60
                            f_image.exposure_time = f'{exposure_time}'
                        else: 
                            f_image.exposure_time = f'1/{exif[2].strip("SS")}'
                        
                        f_image.iso_speed = iso
                        
                        print(photos[index])
                        
                        with open(name+"/"+f'{photos[index]}', 'wb') as new_image_file:
                            new_image_file.write(f_image.get_file())
                        shutil.make_archive(name, 'zip', name)
                        
                    shutil.rmtree(name)
                    
                return send_file(name+'.zip')

            finally:
                os.remove(name+'.zip')
            return render_template('index.html')
    return render_template('index.html')

from flask import send_from_directory

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

if __name__ == '__main__':
    app.debug = True
    app.run()