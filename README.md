# Hand Gesture Recognition

Deep learning based hand gesture recognition using LSTM and MediaPipie.

[Demo video using PingPong Robot](https://youtu.be/g16KvSEq0XU)

![](result/thumb.webp)

<img src="result/result.gif" width="512px">

## Files

Pretrained model in *models* directory.

**create_dataset.py**

Collect dataset from webcam.

**train.ipynp**

Create and train the model using collected dataset.

**test.py**

Test the model using webcam or video.

**robot.py**

Gesture control using PingPong Robot.

## Dependency

- Python 3
- TensorFlow 2.4
- sklearn
- numpy
- OpenCV
- MediaPipe
