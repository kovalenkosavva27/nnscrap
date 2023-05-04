import os
from keras.models import Sequential
from keras.layers import Conv2D 
from keras.layers import MaxPooling2D 
from keras.layers import Flatten 
from keras.layers import Dense 
import cv2
import numpy as np
import tensorflow as tf
from sklearn.metrics import accuracy_score
from skimage import transform
def cnn_classifier():
    cnn = Sequential()
    cnn.add(Conv2D(32, (3,3), input_shape = (50, 50, 3), padding='same', activation = 'relu'))
    cnn.add(MaxPooling2D(pool_size=(2, 2), padding='same'))
    cnn.add(Conv2D(64, (3,3), padding='same', activation = 'relu'))
    cnn.add(MaxPooling2D(pool_size=(2, 2), padding='same'))
    cnn.add(Flatten())
    cnn.add(Dense(500, activation = 'relu'))
    cnn.add(Dense(2, activation = 'softmax'))
    cnn.compile(optimizer = 'adam', loss = 'binary_crossentropy', metrics = ['accuracy'])
    print(cnn.summary())
    return cnn
def reshaped_image(image):
    return transform.resize(image,(50, 50, 3))
def load_images_from_folder():
    Images = os.listdir("catsdogs")
    train_images = []
    train_labels = []
    for image in Images:
            l = [0,0] # [cat,dog]
            if image.find('cat') != -1:
                path = os.path.join("catsdogs/", image)
                img = cv2.imread(path)
                train_images.append(reshaped_image(img))
                l = [1,0]
                train_labels.append(l)
            if image.find('dog') != -1:
                path = os.path.join("catsdogs/", image)
                img = cv2.imread(path)
                train_images.append(reshaped_image(img))
                l = [0,1] 
                train_labels.append(l)
    return np.array(train_images), np.array(train_labels)
def train_test_split(train_data, train_labels, fraction):
    index = int(len(train_data)*fraction)
    return train_data[:index], train_labels[:index], train_data[index:], train_labels[index:]
train_data, train_labels = load_images_from_folder()
fraction = 0.8
train_data, train_labels, test_data, test_labels = train_test_split(train_data, train_labels, fraction)
print ("Train data size: ", len(train_data))
print ("Test data size: ", len(test_data))

cnn = cnn_classifier()

print ("Train data shape: ", train_data.shape)
print ("Test data shape: ", test_data.shape)

idx = np.random.permutation(train_data.shape[0])
cnn.fit(train_data[idx], train_labels[idx], batch_size = 64, epochs = 100)
predicted_test_labels = np.argmax(cnn.predict(test_data), axis=1)
test_labels = np.argmax(test_labels, axis=1)

print ("Actual test labels:", test_labels)
print ("Predicted test labels:", predicted_test_labels)
print ("Accuracy score:", accuracy_score(test_labels, predicted_test_labels))
cnn.save('cats_and_dogs.h5')