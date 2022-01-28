import json, time, sys, cv2, numpy as np
from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer, CvSink
from networktables import NetworkTablesInstance


def calculateCenter(contour):
		M = cv2.moments(contour)
		x = 80
		y= 60
		try:
			x = int(M["m10"] / M["m00"])
		except ZeroDivisionError:
			pass
		try:
			y = int(M["m01"] / M["m00"])
		except ZeroDivisionError:
			pass
		return {"x": x, "y": y}

def pointExtract (point, getX = False, IsY = False):
    assert (getX or IsY)
    if getX:
        return point[0][0]
    elif IsY:
        return point[0][1]


def leftMostPointInContour(contour):
    xPoints = []
    for point in contour:
        xPoints.append(point[0][0])

    minimumPoint = min(xPoints)

    leftPoint = np.where(xPoints == minimumPoint)

    return contour[leftPoint]
    
        

def leftMostContour(contourList):
    xCountours = []
    for contour in contourList:
        print ("contour[0][0][0] : " + str(contour[0][0][0]))
        xCountours.append(leftMostPointInContour(contour)[0][0][0])
    
    minimumContour = min(xCountours)
    leftContour = np.where(xCountours == minimumContour)[0][0]
    print("leftCountour type " + str(type(leftContour)))
    print(leftContour)

    return contourList[leftContour]


def ManipulateHubImage(frame, dashboard):
   # TO-DO
    
    #https://github.com/FRC830/2020Robot/blob/master/vision/vision.py

	# get mask of all values that match bounds, then display part of image that matches bound
	# remove small blobs that may mess up average value
	# https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
	# https://github.com/FRC830/WALL-O/blob/master/vision/vision.py
	# https://www.pyimagesearch.com/2015/01/19/find-distance-camera-objectmarker-using-python-opencv/

    #raise Exception


    img = frame.astype(dtype="uint8")
    hsvImg = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	# read from smartdashboard
    lowerh = dashboard.getNumber("tapeLowerH", 0)
    lowers = dashboard.getNumber("tapeLowerS", 0)
    lowerv = dashboard.getNumber("tapeLowerV", 150)
    upperh = dashboard.getNumber("tapeUpperH", 255)
    uppers = dashboard.getNumber("tapeUpperS", 255)
    upperv = dashboard.getNumber("tapeUpperV", 255)

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
    otherImg, contoursList, countoursMetaData  = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #blobs
	# https://github.com/jrosebr1/imutils/blob/master/imutils/convenience.py#L162
    
    if len(contoursList) < 2:
        return maskOut

    tList = []
    minArea = 50
    for contour in contoursList:
        if cv2.contourArea(contour) > minArea:
            tList.append(contour)
    
    contoursList = tList

    leftBound = leftMostPointInContour(leftMostContour(contoursList))[0][0].any()

    cv2.line(maskOut, (leftBound, 0), (leftBound, 100), (255, 0, 0), thickness=5)

    
    return maskOut