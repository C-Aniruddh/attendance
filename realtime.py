import cv2
import tensorflow as tf, sys

size = 4
webcam = cv2.VideoCapture(0)  # Use camera 0
classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
eye_cascade = cv2.CascadeClassifier('haarcascade_eye.xml')
default_name = ''
score = ''


def getName(fileName):
    image_path = fileName
    # Read in the image_data
    image_data = tf.gfile.FastGFile(image_path, 'rb').read()

    # Loads label file, strips off carriage return
    label_lines = [line.rstrip() for line
                   in tf.gfile.GFile("graphs/retrained_labels.txt")]

    # Unpersists graph from file
    with tf.gfile.FastGFile("graphs/retrained_graph.pb", 'rb') as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())
        _ = tf.import_graph_def(graph_def, name='')

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
        name_person = object_list[0]
    return name_person


while True:
    rval, im = webcam.read()
    im = cv2.flip(im, 1, 0)  # Flip to act as a mirror
    num = 0

    # Resize the image to speed up detection
    mini = cv2.resize(im, (im.shape[1] // size, im.shape[0] // size))

    # detect MultiScale / faces
    faces = classifier.detectMultiScale(mini)
    gray = cv2.cvtColor(im, cv2.COLOR_BGR2GRAY)
    # Draw rectangles around each face
    for f in faces:
        (x, y, w, h) = [v * size for v in f]  # Scale the shapesize backup
        cv2.rectangle(im, (x, y), (x + w, y + h), (0, 255, 0), thickness=4)
        roi_gray = gray[y:y + h, x:x + w]
        roi_color = im[y:y + h, x:x + w]
        # eyes = eye_cascade.detectMultiScale(roi_gray)
        # for (ex,ey,ew,eh) in eyes:
        #    cv2.rectangle(roi_color,(ex,ey),(ex+ew,ey+eh),(0,255,0),2)
        cv2.putText(im, default_name, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255))
        # Save just the rectangle faces in SubRecFaces
        sub_face = im[y:y + h, x:x + w]
        FaceFileName = "unknownfaces/face_" + str(y) + ".jpg"
        cv2.imwrite(FaceFileName, sub_face)
        key = cv2.waitKey(10)
        # if Esc key is press then break out of the loop
        if key == 27:  # The Esc key
            name_person = getName(FaceFileName)
            default_name = name_person
            print(default_name)
            print(score)
            cv2.putText(im, name_person, (x, y), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 255, 255))

    # Show the image
    cv2.imshow('NOVA Face Detection', im)
