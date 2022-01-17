import json, time, sys, cv2, numpy as np
from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer, CvSink
from networktables import NetworkTablesInstance

configFile = "/boot/frc.json"


team = None
server = False
cameraConfigs = []

class CameraConfig: 
    
    self.name = ""
    self.path = ""
    self.streamConfig = ""
    self.config = ""
    def __init__ (self, config):

        # name
        try:
            self.name = config["name"]
        except KeyError:
            parseError("could not read camera name")
            return False

        # path
        try:
            self.path = config["path"]
        except KeyError:
            parseError("camera '{}': could not read path".format(cam.name))
            return False

        # stream properties
        self.streamConfig = config.get("stream")

        self.config = config

        cameraConfigs.append(self)
    
input = CameraServer.getVideo()
output = CameraServer.putVideo('Processed', width, height)

# Table for vision output information
vision_nt = NetworkTables.getTable('Vision')

# Allocating new images is very expensive, always try to preallocate
img = np.zeros(shape=(240, 320, 3), dtype=np.uint8)

while True:
    startTime = time.time()

    frame_time, input_img = input.grabFrame(img)
    output_img = np.copy(input_img)

    # Notify output of error and skip iteration
    if frame_time == 0:
        output.notifyError(input.getError())
        continue

    output = np.copy(input)
    
    hsvImg = cv2.cvtColor(input_img, cv2.COLOR_BGR2HSV)
    maskImg = cv2.inRange(hsv_img, (65, 65, 200), (85, 255, 255)) 

    output.putFrame(maskImg)