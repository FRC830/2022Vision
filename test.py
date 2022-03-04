import json
import time
import sys
import traceback
import numpy as np
import cv2
from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer, CvSink
from networktables import NetworkTablesInstance
import vision2022

def mainRun():
    # start NetworkTables
    ntinst = NetworkTablesInstance.getDefault()
    # ntinst = NetworkTablesInstance.create()
    ntinst.initialize()
    table = ntinst.getTable("vision")
    dashboard = table#table.getSubTable("vision")
    ntinst.startClientTeam(team)

    thing = 99



    while True:
        print ("lopoping")
        dashboard.putNumber("test", thing)
        sleep(1)
        thing += 1