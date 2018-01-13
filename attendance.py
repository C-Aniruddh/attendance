from flask import Flask, render_template, url_for, request, session, redirect, send_from_directory
from flask_pymongo import PyMongo
import bcrypt
import os
from werkzeug.utils import secure_filename
from face_helper import FaceHelper
from face_recognize import FaceRecognize
from helper.attendance import AttendanceHelper
import json
import datetime

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
    user_type = "not_logged"
    if 'username' in session:
        user_status = "logged"
        users = mongo_logins.db.users
        current_user = users.find_one({'name': session['username']})
        user_type = current_user['user_type']
    return render_template('home.html', user_status=user_status, user_type=user_type)


@app.route('/submit', methods=['POST', 'GET'])
def submit():
    if 'username' in session:
        classes = mongo_logins.db.classes
        users = mongo_logins.db.users
        tt = mongo_logins.db.timetable
        if request.method == 'POST':
            file = request.files['image_upload']
            cid = request.form.get('class')
            session['cid'] = cid
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
                session['present'] = present
                session['absent'] = absent

                saplist = range(0, len(sapIDs), 1)
                names = []
                for sap in sapIDs:
                    name = att.getName(sap)
                    names.append(name)

                absentlist = range(0, len(absent), 1)
                absent_names = []
                for absent_sap in absent:
                    absentee = att.getName(absent_sap)
                    absent_names.append(absentee)

                # return json.dumps({'present': present, 'absent': absent})
                return render_template('list.html', saplist=saplist, sap_ids=sapIDs, images=pics, names=names,
                                       absent=absent, absent_name=absent_names, absent_sap=absent,
                                       absentlist=absentlist)
            else:
                return "Invalid file format"

        current_user = users.find_one({'name': session['username']})
        current_user_type = str(current_user['user_type'])
        if current_user_type == 'admin':
            all_classes = classes.find()
            classlist = range(0, all_classes.count(), 1)

            class_ids = []
            class_degrees = []
            class_spec = []
            class_years = []
            if all_classes.count() > 0:
                for c in all_classes:
                    class_id = c['class_id']
                    class_degree = c['degree']
                    class_specialization = c['specialization']
                    class_year = c['year']
                    class_ids.append(class_id)
                    class_degrees.append(class_degree)
                    class_spec.append(class_specialization)
                    class_years.append(class_year)
        else:
            allotted_classes_find = tt.find({'allotted_to': session['username']})
            class_ids = []
            for c in allotted_classes_find:
                if c['class_id'] not in class_ids:
                    class_ids.append(c['class_id'])

            class_degrees = []
            class_spec = []
            class_years = []
            classlist = range(0, len(class_ids), 1)
            if len(class_ids) > 0:
                for a in class_ids:
                    find_class = classes.find_one({'class_id': a})
                    class_degree = find_class['degree']
                    class_specialization = find_class['specialization']
                    class_year = find_class['year']
                    class_degrees.append(class_degree)
                    class_spec.append(class_specialization)
                    class_years.append(class_year)

        return render_template('upload.html', classlist=classlist, class_id=class_ids, class_degree=class_degrees,
                               class_spec=class_spec, class_year=class_years)

    else:
        return redirect('/userlogin')


@app.route('/mark', methods=['POST', 'GET'])
def mark():
    atten = mongo_logins.db.attendance
    classes = mongo_logins.db.classes
    if 'username' in session:
        absent = session['absent']
        present = session['present']
        class_id = session['cid']
        atten_count = atten.find().count()
        atten_id = str(atten_count + 1)
        find_class = classes.find_one({'class_id': class_id})
        class_degree = find_class['degree']
        class_specialization = find_class['specialization']
        class_year = find_class['year']
        date = str(datetime.date.today())
        time = str(datetime.datetime.now().strftime('%H:%M:%S'))
        attendance_name = '%s_%s_%s_%s_%s' % (class_degree, class_specialization, class_year, date, time)
        atten.insert(
            {'date': date, 'submitted_by': session['username'], 'time': time, 'absent': absent, 'present': present,
             'class_id': class_id, 'attendance_name': attendance_name, 'att_id': atten_id})
        return redirect('/')
    else:
        return render_template('404.html')


@app.route('/view_attendance', methods=['POST', 'GET'])
def view_attendance():
    users = mongo_logins.db.users
    atten = mongo_logins.db.attendance
    if 'username' in session:
        current_user = users.find_one({'name': session['username']})
        current_user_type = str(current_user['user_type'])
        if current_user_type == 'admin':
            find_all_records = atten.find()
            attenlist = range(0, find_all_records.count(), 1)
            att_names = []
            att_ids = []

            if find_all_records.count() > 0:
                for r in find_all_records:
                    name = r['attendance_name']
                    id = r['att_id']
                    att_names.append(name)
                    att_ids.append(id)

        else:
            find_all_records = atten.find({'submitted_by': session['username']})
            attenlist = range(0, find_all_records.count(), 1)
            att_names = []
            att_ids = []

            if find_all_records.count() > 0:
                for r in find_all_records:
                    name = r['attendance_name']
                    id = r['att_id']
                    att_names.append(name)
                    att_ids.append(id)
        return render_template('attendance_records.html', attenlist=attenlist, att_id=att_ids, atten_name=att_names)
    else:
        return render_template('404.html')


@app.route('/view_attendance/<att_id>', methods=['POST', 'GET'])
def view(att_id):
    atten = mongo_logins.db.attendance
    classes = mongo_logins.db.classes
    if 'username' in session:
        record = atten.find_one({'att_id': att_id})
        attendance_name = record['attendance_name']
        class_id = record['class_id']
        find_class = classes.find_one({'class_id': class_id})
        class_degree = find_class['degree']
        class_specialization = find_class['specialization']
        class_year = find_class['year']
        class_name = '%s %s %s' % (class_degree, class_specialization, class_year)

        present = list(record['present'])
        absent = list(record['absent'])

        sap_ids = []
        names = []
        status = []
        for student in present:
            sap_ids.append(student)
        for student in absent:
            sap_ids.append(student)

        sap_ids.sort()

        for student in sap_ids:
            if student in present:
                status.append('Present')
            elif student in absent:
                status.append('Absent')
            name = att.getName(student)
            names.append(name)

        attenlist = range(0, len(sap_ids), 1)
        return render_template('attendance.html', attenlist=attenlist, sap_ids=sap_ids, names=names, status=status,
                               class_name=class_name, attendance_name=attendance_name)
    else:
        return render_template('404.html')


@app.route('/timetable', methods=['POST', 'GET'])
def timetable():
    users = mongo_logins.db.users
    if request.method == 'POST':
        faculty = request.form.get('faculty')
        redirection = '/modify_timetable/%s' % faculty
        return redirect(redirection)

    if 'username' in session:
        current_user = users.find_one({'name': session['username']})
        current_user_type = str(current_user['user_type'])
        if current_user_type == 'admin':
            find_faculties = users.find({'user_type': 'faculty'}, {'name': True, 'fullname': True, '_id': False})
            all_faculties = []
            all_faculties_usernames = []
            for person in find_faculties:
                p = person['fullname']
                u = person['name']
                all_faculties.append(p)
                all_faculties_usernames.append(u)

            facultylist = range(0, len(all_faculties), 1)
            return render_template('timetable.html', facultylist=facultylist, faculty_names=all_faculties,
                                   faculty_usernames=all_faculties_usernames)
        else:
            return render_template('500.html')


@app.route('/addclass', methods=['POST', 'GET'])
def addclass():
    classes = mongo_logins.db.classes
    users = mongo_logins.db.users
    if request.method == 'POST':
        current_user = users.find_one({'name': session['username']})
        current_user_type = str(current_user['user_type'])
        if current_user_type == 'admin':
            degree = request.form.get('degree')
            year = request.form.get('year')
            specialization = request.form.get('specialization')
            total_classes = classes.find().count()
            class_id = str(total_classes + 1)
            classes.insert({'class_id': class_id, 'degree': degree, 'year': year, 'specialization': specialization})
            return render_template('add_class.html')
    if 'username' in session:
        return render_template('add_class.html')
    else:
        return render_template('500.html')


@app.route('/modify_timetable/<faculty_username>', methods=['GET', 'POST'])
def modify_timetable(faculty_username):
    users = mongo_logins.db.users
    classes = mongo_logins.db.classes
    tt = mongo_logins.db.timetable
    if request.method == 'POST':
        if 'username' in session:
            current_user = users.find_one({'name': session['username']})
            current_user_type = str(current_user['user_type'])
            if current_user_type == 'admin':
                class_id = request.form.get('class')
                start_time = request.form.get('start_time')
                end_time = request.form.get('end_time')
                day = request.form.get('day')
                redirection = '/modify_timetable/%s' % faculty_username
                tt.insert({'class_id': class_id, 'start_time': start_time, 'end_time': end_time, 'day': day,
                           'allotted_to': faculty_username})
                return redirect(redirection)

    if 'username' in session:
        current_user = users.find_one({'name': session['username']})
        current_user_type = str(current_user['user_type'])
        if current_user_type == 'admin':
            faculty = users.find_one({'name': faculty_username})
            faculty_fullname = faculty['fullname']
            faculty_lectures = tt.find({'allotted_to': faculty_username})
            num_lectures = faculty_lectures.count()
            lecturelist = range(0, num_lectures, 1)
            days = []
            lec_classes = []
            start = []
            end = []

            if num_lectures > 0:
                for l in faculty_lectures:
                    day = l['day']
                    class_id = l['class_id']
                    find_class = classes.find_one({'class_id': class_id})
                    l_class_year = find_class['year']
                    l_class_degree = find_class['degree']
                    l_class_spec = find_class['specialization']
                    l_class_name = '%s - %s - %s' % (l_class_degree, l_class_spec, l_class_year)
                    start_t = l['start_time']
                    end_t = l['end_time']
                    days.append(day)
                    lec_classes.append(l_class_name)
                    start.append(start_t)
                    end.append(end_t)

            all_classes = classes.find()
            classlist = range(0, all_classes.count(), 1)

            class_ids = []
            class_degrees = []
            class_spec = []
            class_years = []
            if all_classes.count() > 0:
                for c in all_classes:
                    class_id = c['class_id']
                    class_degree = c['degree']
                    class_specialization = c['specialization']
                    class_year = c['year']
                    class_ids.append(class_id)
                    class_degrees.append(class_degree)
                    class_spec.append(class_specialization)
                    class_years.append(class_year)

            return render_template('modify_timetable.html', faculty_username=faculty_username,
                                   faculty_name=faculty_fullname, classlist=classlist, class_id=class_ids,
                                   class_degree=class_degrees, class_spec=class_spec, class_year=class_years,
                                   lecturelist=lecturelist, lec_classes=lec_classes, start=start, end=end, days=days)
        else:
            return render_template('500.html')
    return render_template('500.html')


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
                {'fullname': user_fname, 'email': user_email, 'name': request.form.get('username'),
                 'user_type': 'faculty', 'password': hashpass})
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
        if bcrypt.hashpw(request.form.get('password').encode('utf-8'), login_user['password']) == login_user[
            'password']:
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
