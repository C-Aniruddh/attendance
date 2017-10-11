import tensorflow as tf
import os

APP_ROOT = os.path.dirname(os.path.abspath(__file__))
GRAPH_FOLDER = os.path.join(APP_ROOT, 'graphs')


class FaceRecognize:
    def getNames(self, image_list):
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
        return names