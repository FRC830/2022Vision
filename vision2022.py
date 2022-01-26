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



def leftMostPointInContour(contour):
    pointX = []
    for point in contour:
        pointX.append(point[0])

    leftPoint = np.where(pointX == min(pointX))

    return contour[leftPoint]
    
        

def leftMostContour(contourList):
    contourX = []
    for contour in contourList:
        contourX.append(leftMostPointInContour(contour)[0])
    
    leftContour = np.where(contourX == min(contourX))

    return contourList[leftContour]


def ManipulateHubImage(frame, dashboard):
   # TO-DO
    
    #https://github.com/FRC830/2020Robot/blob/master/vision/vision.py

	# get mask of all values that match bounds, then display part of image that matches bound
	# remove small blobs that may mess up average value
	# https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
	# https://github.com/FRC830/WALL-O/blob/master/vision/vision.py
	# https://www.pyimagesearch.com/2015/01/19/find-distance-camera-objectmarker-using-python-opencv/

    print("MANIPULATE HUB IMAGE PETER")

    #raise Exception


    img = frame.astype(dtype="uint8")
    print(img)
    hsvImg = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	# read from smartdashboard
    lowerh = dashboard.getNumber("tapeLowerH", 0)
    lowers = dashboard.getNumber("tapeLowerS", 0)
    lowerv = dashboard.getNumber("tapeLowerV", 0)
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
    
    if len(contoursList) == 0:
        return maskOut   

    leftBound = leftMostPointInContour(leftMostContour(contoursList))[0]

    cv2.line(maskOut, (leftBound, 0), (leftBound, 1), (255, 0, 0), thickness=5)


    

    return maskOut






def ManipulateHubImagePeter(frame, dashboard):
    # TO-DO
    
    #https://github.com/FRC830/2020Robot/blob/master/vision/vision.py

	# get mask of all values that match bounds, then display part of image that matches bound
	# remove small blobs that may mess up average value
	# https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
	# https://github.com/FRC830/WALL-O/blob/master/vision/vision.py
	# https://www.pyimagesearch.com/2015/01/19/find-distance-camera-objectmarker-using-python-opencv/

    print("MANIPULATE HUB IMAGE PETER")

    #raise Exception


    img = frame.astype(dtype="uint8")
    print(img)
    hsvImg = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
	# read from smartdashboard
    lowerh = dashboard.getNumber("tapeLowerH", 0)
    lowers = dashboard.getNumber("tapeLowerS", 0)
    lowerv = dashboard.getNumber("tapeLowerV", 0)
    upperh = dashboard.getNumber("tapeUpperH", 255)
    uppers = dashboard.getNumber("tapeUpperS", 255)
    upperv = dashboard.getNumber("tapeUpperV", 255)
    # lowerh = 15
    # lowers = 100
    # lowerv = 130
    # upperh = 60
    # uppers = 255
    # upperv = 255
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
        print("No countours")
        return maskOut
    print ("In FUNCTION")
    max_contour = max(contours, key=cv2.contourArea)
    if len(contours) > 0:
       ((x, y), radius) = cv2.minEnclosingCircle(max_contour) # returns point, radius
       originalRadius = 7
		#original radius * distance away / width as described in link #3
        #focalLength = (originalRadius * 24.0) / 3.5
		
       if radius > 1:
           center = calculateCenter(max_contour)

           cv2.circle(maskOut, (int(x), int(y)), int(radius), (0, 255, 255), 2)
           cv2.circle(maskOut, (center["x"], center["y"]), 5, (0, 0, 255), -1)
    return maskOut