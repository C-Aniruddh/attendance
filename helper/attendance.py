from flask_pymongo import PyMongo


class AttendanceHelper:

    def __init__(self, mongo_l):
        self.mongo = mongo_l

    def getList(self, names_list):
        faces = self.mongo.db.data
        all_people = faces.find({}, {'sap_id': True, '_id': False})
        all_people_list = []
        for person in all_people:
            p = person['sap_id']
            all_people_list.append(p)
        present = []
        absent = []
        for name in list(all_people_list):
            if name in names_list:
                present.append(name)
            else:
                absent.append(name)

        return present, absent

    def getName(self, sap_id):
        faces = self.mongo.db.data
        person = faces.find_one({'sap_id': sap_id})
        person_name = person['name']
        return person_name
