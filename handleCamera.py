#!/usr/bin/env python3
import json
import time
import sys
import numpy as np
import cv2
from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer, CvSink
from networktables import NetworkTablesInstance

configFile = "/boot/frc.json"

class CameraConfig: pass

team = None
server = False
cameraConfigs = []

"""Report parse error."""
def parseError(str):
	print("config error in '" + configFile + "': " + str, file=sys.stderr)

"""Read single camera configuration."""
def readCameraConfig(config):
	cam = CameraConfig()

	# name
	try:
		cam.name = config["name"]
	except KeyError:
		parseError("could not read camera name")
		return False

	# path
	try:
		cam.path = config["path"]
	except KeyError:
		parseError("camera '{}': could not read path".format(cam.name))
		return False

	# stream properties
	cam.streamConfig = config.get("stream")

	cam.config = config

	cameraConfigs.append(cam)
	return True

"""Read configuration file."""
def readConfig():
	global team
	global server

	# parse file
	try:
		with open(configFile, "rt") as f:
			j = json.load(f)
	except OSError as err:
		print("could not open '{}': {}".format(configFile, err), file=sys.stderr)
		return False

	# top level must be an object
	if not isinstance(j, dict):
		parseError("must be JSON object")
		return False

	# team number
	try:
		team = j["team"]
	except KeyError:
		parseError("could not read team number")
		return False

	# ntmode (optional)
	if "ntmode" in j:
		str = j["ntmode"]
		if str.lower() == "client":
			server = False
		elif str.lower() == "server":
			server = True
		else:
			parseError("could not understand ntmode value '{}'".format(str))

	# cameras
	try:
		cameras = j["cameras"]
	except KeyError:
		parseError("could not read cameras")
		return False
	for camera in cameras:
		if not readCameraConfig(camera):
			return False

	return True

"""Start running the camera."""
def startCamera(config):
	print("Starting camera '{}' on {}".format(config.name, config.path))
	inst = CameraServer.getInstance()
	camera = UsbCamera(config.name, config.path)
	server = inst.startAutomaticCapture(camera=camera, return_server=True)

	camera.setConfigJson(json.dumps(config.config))
	camera.setConnectionStrategy(VideoSource.ConnectionStrategy.kKeepOpen)

	if config.streamConfig is not None:
		server.setConfigJson(json.dumps(config.streamConfig))

	return camera

if __name__ == "__main__":
	if len(sys.argv) >= 2:
		configFile = sys.argv[1]

	# read configuration
	if not readConfig():
		sys.exit(1)

	# start NetworkTables
	ntinst = NetworkTablesInstance.getDefault()
	table = ntinst.getTable("Shuffleboard")
	dashboard = table.getSubTable("vision")
	if server:
		print("Setting up NetworkTables server")
		ntinst.startServer()
	else:
		print("Setting up NetworkTables client for team {}".format(team))
		ntinst.startClientTeam(team)

	# start cameras
	cameras = []
	for cameraConfig in cameraConfigs:
		cameras.append(startCamera(cameraConfig))

	inst = CameraServer.getInstance()
	
	height = 120
	width = 160

	videoOutput = inst.putVideo("Camera Output", width, height)
	visionOutput = inst.putVideo("Vision Processed", width, height)
	videoSink = CvSink("Rasp PI Sink") 


	img = np.ndarray((height,width,3))
	lastfrontCamera = None
	dashboard.putNumber("Number of Cameras", len(cameras))

	# vision processing
	while True:

		frontCamera = dashboard.getBoolean("Front Camera", True)

		if(frontCamera != lastfrontCamera):
			lastfrontCamera = frontCamera 
			if(frontCamera):
				print('Set source 0 (front camera) (ball)')
				videoSink.setSource(cameras[0])
			else:
				print('Set source 1 (back camera) (shooter)')
				videoSink.setSource(cameras[1])


		timestamp, img = videoSink.grabFrame(img) # this outputs a CvImage
		if not timestamp: # could not grab frame
			continue
		videoOutput.putFrame(img)