import glob, os, shutil, sys

fileDir = os.path.dirname(os.path.realpath(__file__))
folders = next(os.walk('.'))[1]
folder_list = list(folders)
folder_list.sort()

for folder in folder_list:
    print("Processing {}".format(folder))
    dir_content = os.listdir(folder)
    print(dir_content)
    count = len(dir_content)
    if count < 10:
        print("Less than 10, making copies")
        for file_o in dir_content:
            for i in range(15-count):
                shutil.copy2('/home/aniruddh/test/server_final/out/{}/{}'.format(folder, file_o), '/home/aniruddh/test/server_final/out/{}/{}_{}.jpg'.format(folder, file_o, i))
                print("Copied {}".format(file_o))
