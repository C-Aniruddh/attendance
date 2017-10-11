from flask_pymongo import PyMongo


class AttendanceHelper:

    def __init__(self, app):
        self.mongo = PyMongo(app)

    def getList(self, names_list):
        faces = self.mongo.db.data
        all_people = faces.find({}, {'name': True, '_id': False})
        all_people_list = []
        for person in all_people:
            p = person['name']
            all_people_list.append(p)
        present = []
        absent = []
        for name in list(all_people_list):
            if name in names_list:
                present.append(name)
            else:
                absent.append(name)

        return present, absent
