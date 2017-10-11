from pymongo import MongoClient

client = MongoClient('mongodb://dbuser:password123@ds157187.mlab.com:57187/')

class dBPopulateHelper:
    def getData(self, name):
        faces = client.heisenberg
        find_person = faces.find_one({'name' : name})