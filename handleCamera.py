#!/usr/bin/env python3
# from asyncio.windows_events import NULL

import json
import time
import sys
import numpy as np
import cv2
from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer, CvSink
from networktables import NetworkTablesInstance
import vision2022

configFile = "/boot/frc.json"

class CameraConfig: pass

team = None
server = True
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

def mainRun():
	#if __name__ == "__main__":
	#print(len(cameraConfigs))
	if len(sys.argv) >= 2:
		configFile = sys.argv[1]

	# read configuration
	if not readConfig():
		sys.exit(1)

	# start NetworkTables
	ntinst = NetworkTablesInstance.getDefault()
	# ntinst = NetworkTablesInstance.create()
	ntinst.initialize()
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
	#following are default values from dashboard
	height = 120 
	width = 160

	videoOutput = inst.putVideo("Camera Output", width, height)
	visionOutput = inst.putVideo("Vision Processed", width, height)
	videoSink = CvSink("Rasp PI Sink")  


	frame = np.ndarray((height,width,3))  #error
	print(type(frame)) # check type of frame
	print(frame) # check contents of frame
	lastfrontCamera = None
	dashboard.putNumber("Number of Cameras", len(cameras))
	
	dashboard.putNumber("tapeLowerH", 0)
	dashboard.putNumber("tapeLowerS", 0)
	dashboard.putNumber("tapeLowerV", 0)
	dashboard.putNumber("tapeUpperH", 255)
	dashboard.putNumber("tapeUpperS", 255)
	dashboard.putNumber("tapeUpperV", 255)

	# vision processing
	while True:
		print("In the while")

		frontCamera = True

		print("Line 158") # debugging
		if(frontCamera != lastfrontCamera):
			print("Line 160") # debugging
			lastfrontCamera = frontCamera 
			print("Line 162") # debugging
			print(lastfrontCamera)
			if(frontCamera):
				print('Set source 0 (front camera) (ball)')
				videoSink.setSource(cameras[0])

		timeout = 0.225
		timestamp, frame = videoSink.grabFrame((120, 160, 3), timeout) # this outputs a CvImage; IS ERROR
		if not timestamp: # could not grab frame
			print("Frame skipped.")
			continue #continue, just to ensure that we don't procsess empty frame
		else:
			print("frame not skipped")

		print ("HEREEEE")

		#*********************************
		#calls to vision Manipulation here, everything above handles vision hardwere configuration

		processedVideo = vision2022.callStuff(frame, dashboard)
		
		videoOutput.putFrame(processedVideo)