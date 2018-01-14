import os, sys, glob, shutil


fileDir = os.path.dirname(os.path.realpath(__file__))
folders = next(os.walk('.'))[1]
folder_list = list(folders)
folder_list.sort()

done = []
for folder in folder_list:
    if folder not in done:
        dir_one = os.listdir(folder)
        dir_one.sort()
        for f in folder_list:
            if f not in done:
                dir_two = os.listdir(f)
                dir_two.sort()
                if dir_one == dir_two:
                    if not (folder==f):
                        print("{} same as {}".format(folder, f))
                        done.append(folder)
                        print("Deleting {}".format(f))
                        if f not in done:
                            if os.path.exists(f):
                                done.append(f)
                                shutil.rmtree(f)
