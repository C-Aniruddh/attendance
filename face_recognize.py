import os
import sys
import pickle
import time
import cv2
import openface

import numpy as np
from sklearn.mixture import GMM

imgDim = 96

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
MODELS_ROOT = os.path.join(APP_ROOT, 'models')

network_model = os.path.join(MODELS_ROOT, 'nn4.small2.v1.t7')
dlibFaceModel = os.path.join(MODELS_ROOT, 'shape_predictor_68_face_landmarks.dat')
classifier_model = os.path.join(MODELS_ROOT, 'classifier.pkl')

align = openface.AlignDlib(dlibFaceModel)
net = openface.TorchNeuralNet(network_model, imgDim=96)

invalid_samples = []


class FaceRecognize:
    """def getNames(self, image_list):
        image_list = list(image_list)
        names = []
        label_lines = [line.rstrip() for line
                       in tf.gfile.GFile(os.path.join(GRAPH_FOLDER, "retrained_labels.txt"))]

        # Unpersists graph from file
        with tf.gfile.FastGFile(os.path.join(GRAPH_FOLDER, "retrained_graph.pb"), 'rb') as f:
            graph_def = tf.GraphDef()
            graph_def.ParseFromString(f.read())
            _ = tf.import_graph_def(graph_def, name='')

        for image in image_list:
            image_data = tf.gfile.FastGFile(image, 'rb').read()
            with tf.Session() as sess:
                # Feed the image_data as input to the graph and get first prediction
                softmax_tensor = sess.graph.get_tensor_by_name('final_result:0')

                predictions = sess.run(softmax_tensor, {'DecodeJpeg/contents:0': image_data})

                # Sort to show labels of first prediction in order of confidence
                top_k = predictions[0].argsort()[-len(predictions[0]):][::-1]
                object_list = []
                for node_id in top_k:
                    human_string = label_lines[node_id]
                    object_list.append(human_string)
                    score = predictions[0][node_id]
                    print('%s (score = %.5f)' % (human_string, score))
                names.append(object_list[0])
        return names"""

    def getRep(self, imgPath, multiple=False):
        start = time.time()
        bgrImg = cv2.imread(imgPath)
        if bgrImg is None:
            raise Exception("Unable to load image: {}".format(imgPath))

        rgbImg = cv2.cvtColor(bgrImg, cv2.COLOR_BGR2RGB)

        if multiple:
            bbs = align.getAllFaceBoundingBoxes(rgbImg)
        else:
            bb1 = align.getLargestFaceBoundingBox(rgbImg)
            bbs = [bb1]
        if len(bbs) == 0 or (not multiple and bb1 is None):
            # raise Exception("Unable to find a face: {}".format(imgPath))
            invalid_samples.append(imgPath)
            pass

        reps = []
        for bb in bbs:
            start = time.time()
            alignedFace = align.align(96, rgbImg, bb, landmarkIndices=openface.AlignDlib.OUTER_EYES_AND_NOSE)
            if alignedFace is None:
                invalid_samples.append(imgPath)
                pass
                # raise Exception("Unable to align image: {}".format(imgPath))
            if imgPath not in invalid_samples:
                start = time.time()
                rep = net.forward(alignedFace)
                reps.append((bb.center().x, rep))

        sreps = sorted(reps, key=lambda x: x[0])
        return sreps

    def getNames(self, image_list, multiple=False):
        with open(classifier_model, 'rb') as f:
            if sys.version_info[0] < 3:
                (le, clf) = pickle.load(f)
            else:
                (le, clf) = pickle.load(f, encoding='latin1')

        names = []
        pics = []
        for img in image_list:
            if img not in invalid_samples:
                print("\n=== {} ===".format(img))
                reps = self.getRep(img, multiple)
                if len(reps) > 1:
                    print("List of faces in image from left to right")
                for r in reps:
                    rep = r[1].reshape(1, -1)
                    bbx = r[0]
                    predictions = clf.predict_proba(rep).ravel()
                    maxI = np.argmax(predictions)
                    person = le.inverse_transform(maxI)
                    confidence = predictions[maxI]
                    name = person.decode('utf-8')
                    if confidence > 0.2 and name not in names:
                        names.append(name)
                        pics.append(os.path.basename(img))
                    if multiple:
                        print("Predict {} @ x={} with {:.2f} confidence.".format(person.decode('utf-8'), bbx,
                                                                                 confidence))
                    else:
                        print("Predict {} with {:.2f} confidence.".format(person.decode('utf-8'), confidence))
                    if isinstance(clf, GMM):
                        dist = np.linalg.norm(rep - clf.means_[maxI])
                        print("  + Distance from the mean: {}".format(dist))
        return names, pics