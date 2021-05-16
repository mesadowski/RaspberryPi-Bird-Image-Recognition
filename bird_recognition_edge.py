# Mhc of this code was stolen from the TF docs, such as:
# https://www.tensorflow.org/tutorials/images/transfer_learning_with_hub
# https://github.com/tensorflow/examples/blob/master/lite/examples/image_classification/raspberry_pi/classify_picamera.py

import os
import time
from PIL import Image,ImageFile

import numpy as np

from tflite_runtime.interpreter import Interpreter

CLASSIFIED_PATH = '/users/michaelsadowski/bird_pics/classified/'
NEW_IMAGES_PATH = '/users/michaelsadowski/bird_pics/new_images/'
MODEL_PATH = '/users/michaelsadowski/tflite_models/model.tflite'
LABELS_PATH = '/users/michaelsadowski/tflite_models/labels.txt'

ImageFile.LOAD_TRUNCATED_IMAGES = True

def load_labels(path):
  with open(path, 'r') as f:
    return {i: line.strip() for i, line in enumerate(f.readlines())}

def set_input_tensor(interpreter, image):
  tensor_index = interpreter.get_input_details()[0]['index']
  input_tensor = interpreter.tensor(tensor_index)()[0]
  input_tensor[:, :] = image

def classify_image(interpreter, image, top_k=1):
  """Returns a sorted array of classification results."""
  set_input_tensor(interpreter, image)
  interpreter.invoke()
  output_details = interpreter.get_output_details()[0]
  output = np.squeeze(interpreter.get_tensor(output_details['index']))

  # If the model is quantized (uint8 data), then dequantize the results
  if output_details['dtype'] == np.uint8:
    scale, zero_point = output_details['quantization']
    output = scale * (output - zero_point)

  ordered = np.argpartition(-output, top_k)
  return [(i, output[i]) for i in ordered[:top_k]]

def main():
    
    labels = load_labels(LABELS_PATH)
    
    interpreter = Interpreter(MODEL_PATH)
    interpreter.allocate_tensors()
    _, height, width, _ = interpreter.get_input_details()[0]['shape']

    while (True):
        filelist = os.listdir(NEW_IMAGES_PATH)
        for f in filelist:
            try:
                #time.sleep(2)   # try to ensure that the file has been released
                image = Image.open(NEW_IMAGES_PATH+f)
                image_resized = image.resize((height,width))
                image_resized.show()
                results = classify_image(interpreter, image_resized)
                label_id, prob = results[0]
                label_name = labels[label_id]
                if prob > 0.3:
                    os.replace(NEW_IMAGES_PATH+f,CLASSIFIED_PATH+label_name+'/'+f)
                else:
                    os.replace(NEW_IMAGES_PATH+f,CLASSIFIED_PATH+'Unsure/'+f)
            except Exception as e:
                print(e)
                print("OS or cropping error")
                raise e   
            #time.sleep(5)

if __name__ == '__main__':
  main()
