from flask import Flask, render_template, url_for, request, session, redirect, send_from_directory
from flask_pymongo import PyMongo
import bcrypt
import os
from werkzeug.utils import secure_filename
from face_helper import FaceHelper
from face_recognize import FaceRecognize
from helper.attendance import AttendanceHelper
import json

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, 'static/uploads')
FACES_FOLDER = os.path.join(APP_ROOT, 'temp_faces')

ALLOWED_EXTENSIONS = {'jpg', 'png', 'jpeg', 'JPG', 'JPEG', 'PNG'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FACES_FOLDER'] = FACES_FOLDER
app.config['MONGO_DBNAME'] = 'faces'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/faces'
app.secret_key = 'mysecret'

facehelper = FaceHelper()
facerecognizer = FaceRecognize()
mongo_logins = PyMongo(app)
att = AttendanceHelper(mongo_logins)


@app.route('/', methods=['POST', 'GET'])
def index():
    user_status = "lol"
    if 'username' in session:
        user_status = "logged"
    return render_template('home.html', user_status=user_status)


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if 'username' in session:
        if request.method == 'POST':
            file = request.files['image_upload']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                fname = filename
                full_path = os.path.join(app.config['UPLOAD_FOLDER'], fname)
                image_faces = facehelper.getFaceFiles(full_path)
                print(image_faces)
                sapIDs, pics = facerecognizer.getNames(image_faces)
                present, absent = att.getList(sapIDs)
                print(str(absent))
                dump = json.dumps({'present': present, 'absent': absent}, indent=4)
                print(dump)

                saplist = range(0, len(sapIDs), 1)
                names = []
                for sap in sapIDs:
                    name = att.getName(sap)
                    names.append(name)

                # return json.dumps({'present': present, 'absent': absent})
                return render_template('list.html', saplist=saplist, sap_ids=sapIDs, images=pics, names=names,
                                       absent=absent)
            else:
                return "Invalid file format"
        return render_template('upload.html')
    else:
        return redirect('/userlogin')


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# Login and registration
@app.route('/register', methods=['POST', 'GET'])
def register():
    if 'username' in session:
        return redirect('/')
    if request.method == 'POST':
        users = mongo_logins.db.users
        user_fname = request.form.get('name')
        # user_fname = request.form['name']
        user_email = request.form.get('email')
        existing_user = users.find_one({'name': request.form.get('username')})
        if existing_user is None:
            hashpass = bcrypt.hashpw(request.form.get('password').encode('utf-8'), bcrypt.gensalt())
            users.insert(
                {'fullname': user_fname, 'email': user_email, 'name': request.form.get('username'), 'password': hashpass})
            session['username'] = request.form.get('username')
            return redirect('/')

        return 'A user with that Email id/username already exists'

    return render_template('register.html')


@app.route('/userlogin', methods=['POST', 'GET'])
def userlogin():
    if 'username' in session:
        return redirect('/')

    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    users = mongo_logins.db.users
    login_user = users.find_one({'name': request.form['username']})

    if login_user:
        if bcrypt.hashpw(request.form.get('password').encode('utf-8'), login_user['password']) == login_user['password']:
            session['username'] = request.form['username']
            return redirect(url_for('index'))

    return 'Invalid username/password combination'


@app.route('/logout')
def logout():
    session.pop('username', None)
    return redirect('/')


@app.route('/face_cdn/<filename>')
def downloads(filename):
    return send_from_directory(app.config['FACES_FOLDER'], filename)


@app.errorhandler(404)
def error404(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def error500(e):
    return render_template('500.html'), 500


if __name__ == '__main__':
    app.secret_key = 'mysecret'
    app.run(host='0.0.0.0', port=8080, debug=True)
