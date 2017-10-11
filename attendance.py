from flask import Flask, render_template, url_for, request, session, redirect, send_from_directory
import os
from werkzeug.utils import secure_filename
from face_helper import FaceHelper
from face_recognize import FaceRecognize
from helper.attendance import AttendanceHelper
import json

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')
GRAPH_FOLDER = os.path.join(APP_ROOT, 'graphs')


ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg'}


app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GRAPH_FOLDER'] = GRAPH_FOLDER
app.config['MONGO_DBNAME'] = 'faces'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/faces'

@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if request.method == 'POST':
        file = request.files['song_upload']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            fname = filename
            full_path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
            facehelper = FaceHelper()
            image_faces = facehelper.getFaceFiles(full_path)
            print(image_faces)
            facerecognizer = FaceRecognize()
            names = facerecognizer.getNames(image_faces)
            att = AttendanceHelper(app)
            present, absent = att.getList(names)
            print(str(absent))
            dump = json.dumps({'present':present, 'absent':absent}, indent=4)
            print(dump)
            return json.dumps({'present' : present, 'absent' : absent})
    return render_template('submit.html')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
