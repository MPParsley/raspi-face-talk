#!/usr/bin/python
"""
This program is demonstration for face and object detection using haar-like features.
The program finds faces in a camera image or video stream and displays a red box around them.

Python implementation by: Roman Stanchak, James Bowman
"""
import sys
import cv2.cv as cv
from optparse import OptionParser
import os

# Parameters for haar detection
# From the API:
# The default parameters (scale_factor=2, min_neighbors=3, flags=0) are tuned 
# for accurate yet slow object detection. For a faster operation on real video 
# images the settings are: 
# scale_factor=1.2, min_neighbors=2, flags=CV_HAAR_DO_CANNY_PRUNING, 
# min_size=<minimum possible face size

min_size = (2, 2)
image_scale = 2
haar_scale = 1.2
min_neighbors = 2
haar_flags = 0


def map(value, leftMin, leftMax, rightMin, rightMax):
	leftSpan = leftMax - leftMin
	rightSpan = rightMax - rightMin
	valueScaled = float(value - leftMin) / float(leftSpan)
	return rightMin + (valueScaled * rightSpan)

def detect_and_draw(img, cascade, detected):
    # allocate temporary images
    gray = cv.CreateImage((img.width,img.height), 8, 1)
    small_img = cv.CreateImage((cv.Round(img.width / image_scale), cv.Round (img.height / image_scale)), 8, 1)

    # convert color input image to grayscale
    cv.CvtColor(img, gray, cv.CV_BGR2GRAY)

    # scale input image for faster processing
    cv.Resize(gray, small_img, cv.CV_INTER_LINEAR)

    cv.EqualizeHist(small_img, small_img)

    if(cascade):
        t = cv.GetTickCount()
        faces = cv.HaarDetectObjects(small_img, cascade, cv.CreateMemStorage(0), haar_scale, min_neighbors, haar_flags, min_size)
        t = cv.GetTickCount() - t
        print "detection time = %gms" % (t/(cv.GetTickFrequency()*1000.))
        if faces:
	    if detected == 0:
		# os.system('festival --tts hi &')
		detected = 1
            for ((x, y, w, h), n) in faces:
                # the input to cv.HaarDetectObjects was resized, so scale the 
                # bounding box of each face and convert it to two CvPoints
                pt1 = (int(x * image_scale), int(y * image_scale))
                pt2 = (int((x + w) * image_scale), int((y + h) * image_scale))
                cv.Rectangle(img, pt1, pt2, cv.RGB(255, 0, 0), 3, 8, 0)
		span = (pt1[0] + pt2[0]) / 2
		stlt = (pt1[1] + pt2[1]) / 2
		#valPan = map(span, 0, 320, 0.09, 0.18)
		#valTilt = map(stlt, 0, 240, 0.09, 0.18)
		valPan = map(span, 0, 320, 0.11, 0.15)
		valTilt = map(stlt, 0, 240, 0.10, 0.14)
		#print valPan, valTilt
		print "Face at: ", pt1[0], ",", pt2[0], "\t", pt1[1], ",", pt2[1]

		if span < 150:
			 print "left"
		if span > 150: 
			 print "right"

		#os.system('echo "6="' + str(valTilt) + ' > /dev/pi-blaster')
		#os.system('echo "7="' + str(valPan) + ' > /dev/pi-blaster')
	else:
		if detected == 1:
			#print "Last seen at: ", pt1[0], ",", pt2[0], "\t", pt1[1], ",", pt2[1]
			#os.system('festival --tts bye &')
			status = "just disappeared"
		detected = 0

    cv.ShowImage("result", img)
    return detected

if __name__ == '__main__':
    parser = OptionParser(usage = "usage: %prog [options] [filename|camera_index]")
    parser.add_option("-c", "--cascade", action="store", dest="cascade", type="str", help="Haar cascade file, default %default", default = "../data/haarcascades/haarcascade_frontalface_alt.xml")
    (options, args) = parser.parse_args()

    cascade = cv.Load(options.cascade)
    
    cv.NamedWindow("result", 1)

    width = 320 #leave None for auto-detection
    height = 240 #leave None for auto-detection


    if True:
	detected = 0
        frame_copy = None
        while True:

	    os.system("raspistill -t 0 -hf -rot 180 -p -99,-99,100,100 -o /run/shm/image.jpg -w 320 -h 240 ")
   	    frame=cv.LoadImage('/run/shm/image.jpg',cv.CV_LOAD_IMAGE_COLOR)
	    frame_copy=frame
            if not frame:
                break
            if not frame_copy:
                frame_copy = cv.CreateImage((frame.width,frame.height), cv.IPL_DEPTH_8U, frame.nChannels)

            if frame.origin == cv.IPL_ORIGIN_TL:
                cv.Copy(frame, frame_copy)
            else:
                cv.Flip(frame, frame_copy, 0)
            
            detected = detect_and_draw(frame_copy, cascade, detected)

            if cv.WaitKey(10) >= 0:
                break

    cv.DestroyWindow("result")
