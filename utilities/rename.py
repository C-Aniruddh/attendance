import glob, os, sys, shutil

fileDir = os.path.dirname(os.path.realpath(__file__))
folders = next(os.walk('.'))[1]
folder_list = list(folders)
folder_list.sort()

initial_num = 70061016000
for f in folder_list:
    initial_num= initial_num+1
    shutil.move(f, str(initial_num))
