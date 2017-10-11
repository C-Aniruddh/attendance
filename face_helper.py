import cv2
import numpy as np
import os

ROOT = os.path.dirname(os.path.abspath(__file__))
size = 4
classifier = cv2.CascadeClassifier(os.path.join(ROOT, "haarcascade_frontalface_default.xml"))
APP_ROOT = os.path.dirname(os.path.abspath(__file__))


class FaceHelper:
    def getFaceFiles(self, image_path):
        im = cv2.imread(image_path)
        im = cv2.flip(im, 1, 0)  # Flip to act as a mirror

        # Resize the image to speed up detection
        mini = cv2.resize(im, (im.shape[1] // size, im.shape[0] // size))

        # detect MultiScale / faces
        faces = classifier.detectMultiScale(mini)

        image_filenames = []
        for f in faces:
            (x, y, w, h) = [v * size for v in f]  # Scale the shapesize backup
            cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), thickness=4)
            # Save just the rectangle faces in SubRecFaces
            sub_face = im[y:y + h, x:x + w]
            FaceFileName = os.path.join(ROOT, "temp_faces/face_") + str(y) + ".jpg"
            cv2.imwrite(FaceFileName, sub_face)
            if os.path.exists(FaceFileName):
                image_filenames.append(FaceFileName)

        return image_filenames