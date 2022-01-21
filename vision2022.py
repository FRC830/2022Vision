import json, time, sys, cv2, numpy as np
from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer, CvSink
from networktables import NetworkTablesInstance


def ManipulateHubImage(frame):
    # TO-DO
    
    #https://github.com/FRC830/2020Robot/blob/master/vision/vision.py

	# get mask of all values that match bounds, then display part of image that matches bound
	# remove small blobs that may mess up average value
	# https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
	# https://github.com/FRC830/WALL-O/blob/master/vision/vision.py
	# https://www.pyimagesearch.com/2015/01/19/find-distance-camera-objectmarker-using-python-opencv/

    readableImage = frame.astype(dtype="uint8")
    hsvImg = cv2.cvtColor(readableImage, cv2.COLOR_BGR2HSV)
	# read from smartdashboard
    targeth = 166
    targets = 11
    targetv = 100
    upperTolerenceh = 10
    upperTolerences = 10
    upperTolerencev = 10
    lowerTolerenceh = 10
    lowerTolerences = 10
    lowerTolerencev = 10
    lowerBound = np.array([targeth-lowerToleranceh, targets-lowerTolerances, targetv-lowerTolerancev])
    upperBound = np.array([targeth+upperToleranceh, targets+upperTolerances, targetv+upperTolerancev])

    mask = cv2.inrange(hsvImg, lowerBound, upperBound)

    maskOut = cv2.bitwise_and(readableImage, readableImage, mask=mask)

    return maskOut









def ManipulateHubImagePeter(frame):
    # TO-DO
    
    #https://github.com/FRC830/2020Robot/blob/master/vision/vision.py

	# get mask of all values that match bounds, then display part of image that matches bound
	# remove small blobs that may mess up average value
	# https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
	# https://github.com/FRC830/WALL-O/blob/master/vision/vision.py
	# https://www.pyimagesearch.com/2015/01/19/find-distance-camera-objectmarker-using-python-opencv/

    
    
    img = (frame[0].astype(dtype="uint8"), frame[1].astype(dtype="uint8"), frame[2].astype(dtype="uint8"))
    print(img)
    hsvImg = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	# read from smartdashboard
    lowerh = 15
    lowers = 100
    lowerv = 130
    upperh = 60
    uppers = 255
    upperv = 255
    lowerBound = np.array([lowerh, lowers, lowerv])
    upperBound = np.array([upperh, uppers, upperv])
	# get mask of all values that match bounds, then display part of image that matches bound
    mask = cv2.inRange(hsvImg, lowerBound, upperBound)
	# remove small blobs that may mess up average value
	# https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
	# https://github.com/FRC830/WALL-O/blob/master/vision/vision.py
	# https://www.pyimagesearch.com/2015/01/19/find-distance-camera-objectmarker-using-python-opencv/

    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)
    maskOut = cv2.bitwise_and(img, img, mask=mask)
	# Find 'parent' contour(s) with simple chain countour algorithm
    contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #blobs
	# https://github.com/jrosebr1/imutils/blob/master/imutils/convenience.py#L162
    contours = contours[1] 
    if len(contours) == 0:
        return maskOut
    max_contour = max(contours, key=cv2.contourArea)
    if len(contours) > 0:
        ((x, y), radius) = cv2.minEnclosingCircle(max_contour) # returns point, radius
        originalRadius = 7
		# original radius * distance away / width as described in link #3
        # focalLength = (originalRadius * 24.0) / 3.5
		
        #if radius > 1:
            #center = calculateCenter(max_contour)
            #dashboard.putNumber("centerXball", center["x"])

            #cv2.circle(maskOut, (int(x), int(y)), int(radius), (0, 255, 255), 2)
            #cv2.circle(maskOut, (center["x"], center["y"]), 5, (0, 0, 255), -1)
        #else:
            #dashboard.putNumber("centerXball", 80) # center so it wont do anything
	
    return maskOut