import cv2
import numpy as np
import os
import dlib
from datetime import datetime

ROOT = os.path.dirname(os.path.abspath(__file__))
size = 4

# classifier = cv2.CascadeClassifier(os.path.join(ROOT, "haarcascade_frontalface_default.xml"))
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
predictor_path = os.path.join(APP_ROOT, 'models', 'shape_predictor_68_face_landmarks.dat')

detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor(predictor_path)


class FaceHelper:
    """def getFaceFiles(self, image_path):
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

        return image_filenames"""

    def getFaceFiles(self, image_path):
        face_id = 0
        img = cv2.imread(image_path)
        mini = cv2.resize(img, (img.shape[1] // size, img.shape[0] // size))
        gray = cv2.cvtColor(mini, cv2.COLOR_BGR2GRAY)

        images = []
        # win.clear_overlay()
        # win.set_image(img)

        # Ask the detector to find the bounding boxes of each face. The 1 in the
        # second argument indicates that we should upsample the image 1 time. This
        # will make everything bigger and allow us to detect more faces.
        dets = detector(gray, 1)
        print("Number of faces detected: {}".format(len(dets)))
        for k, d in enumerate(dets):
            print("Detection {}: Left: {} Top: {} Right: {} Bottom: {}".format(
                k, d.left(), d.top(), d.right(), d.bottom()))
            # Get the landmarks/parts for the face in box d.
            shape = predictor(mini, d)
            print("Part 0: {}, Part 1: {} ...".format(shape.part(0),
                                                      shape.part(1)))
            # Save the new face
            crop = mini[d.top()-10:d.bottom()+10, d.left()-10:d.right()+10]
            if crop.shape[0] > 0 and crop.shape[1] > 0:
                time = datetime.utcnow().strftime('%Y-%m-%d-%H-%M-%S-%f')[:-3]
                print("Saving face.")
                save_img = cv2.resize(crop, (256, 256))
                file_name = 'face_%s_%s.jpg' % (face_id, time)
                cv2.imwrite(os.path.join(ROOT, 'temp_faces', file_name), save_img)
                full_path = str(os.path.join(ROOT, 'temp_faces', file_name))
                images.append(full_path)
                face_id = face_id + 1

        return images
