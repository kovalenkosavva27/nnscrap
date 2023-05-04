import os
import cv2
import numpy as np
from skimage import transform
import tensorflow as tf
import keras
from tkinter.filedialog import askopenfilename
def load_image(filename):
    train_images = []
    path = filename
    img = cv2.imread(path)
    train_images.append(reshaped_image(img))
    return np.array(train_images)
def reshaped_image(image):
    return transform.resize(image,(50, 50, 3))
filename = askopenfilename()
from pathlib import Path
train_data = load_image(Path(filename).stem+'.jpg')
cnn=keras.models.load_model('cats_and_dogs.h5')
x=tf.expand_dims(train_data[0],axis=0)
y=cnn(x)
print('cat' if y.numpy()[0][0]>y.numpy()[0][1] else 'dog')