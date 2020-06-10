# gesture_recognition_ee292d
ML model to recognize letters drawn out in space with the Arduino 33 BLE. (Stanford EE292D Final Project, Spring 2020)

This repo contains scripts for data collection, preprocessing, model training, TFLite model inference, model deployment on Arduino, and finally autocorrect. The main structure of the project is to classify (sequence_len, 3) samples of accelerometer data over time as one of a set of known gestures. The final model is saved as a TFLite model, and this can be run either on a computer reading accelerometer data through Serial or deployed to Arduino. We completed this project in the following steps:


## 1. Data Collection

Save accelerometer recordings to csv files
```shell
$ python data_collect.py 
```

Preprocess data to (sequence_len, 3) samples, stored with many recordings in a .txt file per person
execute cells in chunk_data.ipynb 
```shell
$ jupyter notebook chunk_data.ipynb
```

To visualize data:
```shell
$ cd drawData
$ python drawData3D.py
```


## 2. Train a Model
Train a model using code in repo: https://github.com/katherinekowalski/tensorflow/tree/master/tensorflow/lite/micro/examples/magic_wand/train
Follow instructions in README there


## 3. Test a Model on Real Data

On a computer, test inference + autocorrect
Update desired weight file path and corresponding classes in Inference/inference.py then:
```shell
$ cd Inference
$ python spell.py
```

On an Arduino, test inference using code in gesture_recognition folder
Required Libraries: TensorflowLite, appropriate IMU library for your Arduino
Open and run gesture_recognition.ino





