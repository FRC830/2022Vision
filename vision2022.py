import json, time, sys, cv2, numpy as np
import math
from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer, CvSink
from networktables import NetworkTablesInstance


def calculateCenter(contour):
		M = cv2.moments(contour)
		x = 80
		y = 60
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

#find closest either gap or tape
def findCenter(tapes, gaps, maskOut, tapeToGapRatio):

    assert(len(tapes) == (len(gaps)+1))

    closestObjectIndex=0
    closestIsTape=True

    for index,tape in enumerate(tapes):
        width= tape[3]
        widestWidthSoFar = tapes[closestObjectIndex][3]
        if not index == 0:
            if(width > widestWidthSoFar):
                closestObjectIndex=index
    

    for index,gap in enumerate(gaps):
        width= gap[1] - gap[0]

        if(closestIsTape):
            widestWidthSoFar = tapes[closestObjectIndex][3]
        else:
            widestWidthSoFar = gaps[closestObjectIndex][1] - gaps[closestObjectIndex][0]
        #print(width)
        if ((width*tapeToGapRatio)>widestWidthSoFar):
            closestObjectIndex = index
            closestIsTape = False

    i = 60
    if(closestIsTape):
        #print(str(len(tapes))+","+str(closestObjectIndex))
        contourObject=tapes[closestObjectIndex]
        cv2.rectangle(maskOut,(contourObject[1],contourObject[2]),(contourObject[1]+contourObject[3],contourObject[2]+contourObject[4]),(0,0,255),2)

        if(closestObjectIndex == 0 or closestObjectIndex == len(tapes) - 1):
            return


        closestObjectWidth = tapes[closestObjectIndex][3]
        leftObjectWidth = (gaps[closestObjectIndex-1][1]-gaps[closestObjectIndex-1][0])*tapeToGapRatio
        rightObjectWidth = (gaps[closestObjectIndex][1]-gaps[closestObjectIndex][0])*tapeToGapRatio

        #cv2.putText(maskOut, str(int(closestObjectWidth)), (tapes[closestObjectIndex][1]+(int)(closestObjectWidth/2), tapes[closestObjectIndex][2]-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (102,51,159))
        #cv2.putText(maskOut, str(int(leftObjectWidth)), (gaps[closestObjectIndex-1][1],   tapes[closestObjectIndex][2]-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (102,51,159))
        #cv2.putText(maskOut, str(int(rightObjectWidth)), (gaps[closestObjectIndex][1],  tapes[closestObjectIndex][2]-20), cv2.FONT_HERSHEY_SIMPLEX, 1, (102,51,159))
        cv2.putText(maskOut, str(closestObjectWidth), (30, 2*i), cv2.FONT_HERSHEY_SIMPLEX, 1, (102,51,159))
        cv2.putText(maskOut, str(leftObjectWidth), (30,   i), cv2.FONT_HERSHEY_SIMPLEX, 1, (102,51,159))
        cv2.putText(maskOut, str(rightObjectWidth), (30,  3*i), cv2.FONT_HERSHEY_SIMPLEX, 1, (102,51,159))

    else:
        try:
            height= tapes[closestObjectIndex+1][2]
        except Exception as e:
            height=100
            print("not enough tapes")
            return
        cv2.rectangle(maskOut, (gaps[closestObjectIndex][0], height), (gaps[closestObjectIndex][1], height-5), (0,0,255), 5)


        closestObjectWidth = gaps[closestObjectIndex][1] - gaps[closestObjectIndex][0]
        leftObjectWidth = tapes[closestObjectIndex][3] / tapeToGapRatio
        rightObjectWidth = tapes[closestObjectIndex + 1][3] / tapeToGapRatio

        cv2.putText(maskOut, str(closestObjectWidth), (30, 2 * i), cv2.FONT_HERSHEY_SIMPLEX, 1, (102, 51, 159))
        cv2.putText(maskOut, str(leftObjectWidth), (30, i), cv2.FONT_HERSHEY_SIMPLEX, 1, (102, 51, 159))
        cv2.putText(maskOut, str(rightObjectWidth),(30,3*i), cv2.FONT_HERSHEY_SIMPLEX, 1, (102, 51, 159))

    expectedSideObjectWidth = (leftObjectWidth+rightObjectWidth) / 2
    centerResidual = closestObjectWidth-expectedSideObjectWidth
    if(leftObjectWidth>expectedSideObjectWidth):
        leftObjectResidual = leftObjectWidth-expectedSideObjectWidth
        proportionAwayFromCenter =- leftObjectResidual / centerResidual
        
    else:
        rightObjectResidual=rightObjectWidth-expectedSideObjectWidth
        proportionAwayFromCenter=rightObjectResidual / centerResidual
    
    proportionAwayFromCenter = min(1, proportionAwayFromCenter)
    proportionAwayFromCenter = max(-1, proportionAwayFromCenter)

    if(closestIsTape):
        distanceFromCenterToEdge=(tapes[closestObjectIndex][3]/2)
        centerOfClosestObject= tapes[closestObjectIndex][1]+distanceFromCenterToEdge
        
    else:
        distanceFromCenterToEdge=(gaps[closestObjectIndex][1]-gaps[closestObjectIndex][0])/2
        centerOfClosestObject= gaps[closestObjectIndex][0]+distanceFromCenterToEdge


    trueCenter=(int)(centerOfClosestObject+(proportionAwayFromCenter*distanceFromCenterToEdge))
    cv2.line(maskOut,(trueCenter,0),(trueCenter,720),(255,255,255),3)

    return trueCenter


def findDistance(maskOut,tapes,dashboard):
    #find how high on the image the tapes are 
    heightOfHubOnCamera = tapes[0][2]
    for tape in tapes:
        heightOfHubOnCamera=min(heightOfHubOnCamera,tape[2])
    
    topAngle = dashboard.getNumber("CameraAngle", 20) + dashboard.getNumber("CameraVerticleFOV", 35) / 2
    bottomAngle =  dashboard.getNumber("CameraAngle", 20) - dashboard.getNumber("CameraVerticleFOV", 35) / 2

    hubPosProportionOfScreen = heightOfHubOnCamera/720
    hubAngleFromTop = hubPosProportionOfScreen*dashboard.getNumber("CameraVerticleFOV",35)

    hubAngle = topAngle - hubAngleFromTop

    hubAngleInRadians= hubAngle*math.pi/180

    hubHeightDifference=104-dashboard.getNumber("CameraHeight",42)

    distanceToHub=hubHeightDifference/(math.tan(hubAngleInRadians)) 

    return distanceToHub


    

#place the robot 15 feet away
def calebrateAngle(maskOut,tapes,dashboard):

    hubHeightDifference=104-dashboard.getNumber("CameraHeight",42)

    targetHubAngle=math.atan(hubHeightDifference/dashboard.getNumber("CalibrationDistance",180))*180/math.pi

    heightOfHubOnCamera = tapes[0][2]

    for tape in tapes:
        heightOfHubOnCamera=min(heightOfHubOnCamera,tape[2])
    
    topAngle = dashboard.getNumber("CameraAngle", 20) + dashboard.getNumber("CameraVerticleFOV", 35)/2
    bottomAngle =  dashboard.getNumber("CameraAngle", 20) -  dashboard.getNumber("CameraVerticleFOV", 35)/2

    hubPosProportionOfScreen = heightOfHubOnCamera/720
    hubAngleFromTop = hubPosProportionOfScreen*dashboard.getNumber("CameraVerticleFOV", 35)

    hubAngle = topAngle - hubAngleFromTop

    print("the angle should be "+str(dashboard.getNumber("CameraAngle", 20)+(targetHubAngle-hubAngle)))

    return

def findDistance(maskOut,tapes,dashboard):
    #find how high on the image the tapes are 
    heightOfHubOnCamera = tapes[0][2]
    for tape in tapes:
        heightOfHubOnCamera=min(heightOfHubOnCamera,tape[2])
    
    topAngle = dashboard.getNumber("CameraAngle",20) + dashboard.getNumber("CameraVerticleFOV",35)/2
    bottomAngle =  dashboard.getNumber("CameraAngle",20) -  dashboard.getNumber("CameraVerticleFOV",35)/2

    hubPosProportionOfScreen = heightOfHubOnCamera/720
    hubAngleFromTop = hubPosProportionOfScreen*dashboard.getNumber("CameraVerticleFOV",35)

    hubAngle = topAngle - hubAngleFromTop

    hubAngleInRadians= hubAngle*math.pi/180

    hubHeightDifference=104-dashboard.getNumber("CameraHeight",42)

    distanceToHub=hubHeightDifference/(math.tan(hubAngleInRadians)) 

    return distanceToHub


    

#place the robot 15 feet away
def calebrateAngle(maskOut,tapes,dashboard):

    hubHeightDifference=104-dashboard.getNumber("CameraHeight",42)

    targetHubAngle=math.atan(hubHeightDifference/dashboard.getNumber("CalibrationDistance",180))*180/math.pi

    heightOfHubOnCamera = tapes[0][2]

    for tape in tapes:
        heightOfHubOnCamera=min(heightOfHubOnCamera,tape[2])
    
    topAngle = dashboard.getNumber("CameraAngle", 20) + dashboard.getNumber("CameraVerticleFOV", 35)/2
    bottomAngle =  dashboard.getNumber("CameraAngle", 20) -  dashboard.getNumber("CameraVerticleFOV", 35)/2

    hubPosProportionOfScreen = heightOfHubOnCamera/720
    hubAngleFromTop = hubPosProportionOfScreen*dashboard.getNumber("CameraVerticleFOV", 35)

    hubAngle = topAngle - hubAngleFromTop

    print("the angle should be "+str(dashboard.getNumber("CameraAngle", 20)+(targetHubAngle-hubAngle)))

    return

    


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
    lowerh = dashboard.getNumber("tapeLowerH", 40)
    lowers = dashboard.getNumber("tapeLowerS", 150)
    lowerv = dashboard.getNumber("tapeLowerV", 100)
    upperh = dashboard.getNumber("tapeUpperH", 80)
    uppers = dashboard.getNumber("tapeUpperS", 255)
    upperv = dashboard.getNumber("tapeUpperV", 255)
    tapeToGapRatio = dashboard.getNumber("tapeToGapRatio",(10/11))

    lowerBound = np.array([lowerh, lowers, lowerv])
    upperBound = np.array([upperh, uppers, upperv])
	# get mask of all values that match bounds, then display part of image that matches bound
    mask = cv2.inRange(hsvImg, lowerBound, upperBound)
	# remove small blobs that may mess up average value
	# https://www.pyimagesearch.com/2015/09/14/ball-tracking-with-opencv/
	# https://github.com/FRC830/WALL-O/blob/master/vision/vision.py
	# https://www.pyimagesearch.com/2015/01/19/find-distance-camera-objectmarker-using-python-opencv/

    #mask = cv2.erode(mask, None, iterations=2)
    #mask = cv2.dilate(mask, None, iterations=2)
    
    maskOut = img# cv2.bitwise_and(img, img, mask=mask)
	# Find 'parent' contour(s) with simple chain countour algorithm
    otherImg, contoursList, countoursMetaData  = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) #blobs
	# https://github.com/jrosebr1/imutils/blob/master/imutils/convenience.py#L162
    
    if len(contoursList) < 2:

        cv2.line(maskOut,(0,360),(1280,360),(255,0,0),3)
        dashboard.putNumber("Hub Center X Distance", -1)
        return maskOut

    xSortedObjectsList =[]
    xSortedGaps = []
    tempList = []
    minArea = 20
    for contour in contoursList:
        if cv2.contourArea(contour) > minArea:
            tempList.append(contour)
            x,y,w,h = cv2.boundingRect(contour)
            a = cv2.contourArea(contour)

            if len(xSortedObjectsList) == 0:
                xSortedObjectsList.append((contour,x,y,w,h,a))
            else:
                insertionIndex=0
                for index, i in enumerate(xSortedObjectsList):
                    if(x>i[1]):
                        insertionIndex=index+1
                        
                xSortedObjectsList.insert(insertionIndex,(contour,x,y,w,h,a))

    if len(xSortedObjectsList) < 2:
        dashboard.putNumber("Hub Center X Distance", -1)
        return maskOut

    for index, i in enumerate(xSortedObjectsList):
        if index != 0:
        
            

            leftGapBound=xSortedObjectsList[index-1][1]+xSortedObjectsList[index-1][3]
            rightGapBound=i[1]
            xSortedGaps.append((leftGapBound,rightGapBound))
            image = cv2.rectangle(maskOut, (leftGapBound, i[2]), (rightGapBound, i[2]-5), (255,0,0), 5)

    

    for index, contourObject in enumerate(xSortedObjectsList):
        cv2.rectangle(maskOut,(contourObject[1],contourObject[2]),(contourObject[1]+contourObject[3],contourObject[2]+contourObject[4]),(0,100+(index*(155/len(xSortedObjectsList))),0),2)

    

    
    dashboard.putNumber("Hub Center X Distance", findCenter(xSortedObjectsList,xSortedGaps,maskOut,tapeToGapRatio))

    
    contoursList = tempList

    #leftBound = leftMostPointInContour(leftMostContour(contoursList))[0][0].any()

    #cv2.line(maskOut, (leftBound, 0), (leftBound, 100), (255, 0, 0), thickness=5)

    print(findDistance(maskOut,xSortedObjectsList,dashboard))

    
    return maskOut