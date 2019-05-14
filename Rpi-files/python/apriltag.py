from __future__ import division
from __future__ import print_function
from imutils.video import VideoStream
import imutils
import numpy as np
import cv2 as cv
import RPi.GPIO as rp
from time import sleep
from argparse import ArgumentParser
import apriltag
##############################
def map( x, in_min,in_max, out_min, out_max):
    maps = -((x - in_max)*(out_max-out_min)/(in_max-in_min)+out_min)
    return maps
##############################
parser = ArgumentParser(description='test apriltag Python bindings')
parser.add_argument('device_or_movie', metavar='INPUT', nargs='?', default=0,help='Movie to load or integer ID of camera device')
apriltag.add_arguments(parser)
options = parser.parse_args()
detector = apriltag.Detector(options,searchpath=apriltag._get_demo_searchpath())
##############################
servo1 = 15
servo2 = 14
deltadt = 0.1
dt1 = 4
dt2 = 6
cv.namedWindow('window')
tagid = 8
##############################
rp.setmode(rp.BCM)
rp.setwarnings(False)
rp.setup(servo1,rp.OUT)
rp.setup(servo2,rp.OUT)
pwm1 = rp.PWM(servo1,50)
pwm2 = rp.PWM(servo2,50)
pwm1.start(2)
pwm2.start(6)
##############################
cv.namedWindow('frame',cv.WINDOW_FREERATIO)
usingPiCamera = True
vs = VideoStream(src=0, usePiCamera=usingPiCamera, resolution=(240, 240),
	framerate=60).start()
sleep(0.2)
##############################
while True:
    frame = vs.read()
    if not usingPiCamera:
	    frame = imutils.resize(frame, width=frameSize[0])
    ################  
    mrkzy = int(len(frame)/2)
    mrkzx = int(len(frame[0])/2)
    fry = int(len(frame))
    frx = int(len(frame[0]))
    cntx = 9999  
    cnty = 9999
    ################
    gray = cv.cvtColor(frame, cv.COLOR_RGB2GRAY)
    detections, dimg = detector.detect(gray, return_image=True)
    hilight = frame // 2 + dimg[:, :, None] // 2 
    ##############################
    try:
        for L in range (len(detections)):
            dtid = detections[L][1]
            print(dtid)
            if (dtid == tagid):
                dtcord = detections[L][6]
                aprilx = int(detections[L][6][0])
                aprily = int(detections[L][6][1])
                center = (aprilx,aprily)
                radius = int(aprilx - detections[L][7][0][0])
                if (radius < 0):
                    radius = -radius
                cv.circle(frame,center,radius,(0,0,255),2)
                cv.circle(frame,center,2,(255,0,0),4)
                cntx = int(aprilx)  
                cnty = int(aprily)
        ##############################
        if(cntx == 9999 or cnty == 9999):
            notfound + 3
        else:
            errx = mrkzx - cntx
            erry = mrkzy - cnty
        ##############################
            dtx = errx / (frx*2)
            dty = erry / (fry*2)
            dtx = (int(dtx*ksa))/ksa
            dty = (int(dty*ksa))/ksa
            timex = (int(map(dtx,mrkzx,0,0,1)*kti))/kti
            timey = (int(map(dty,mrkzy,0,0,1)*kti))/kti
            ################
            if (dtx >= 0):
                servx = np.arange(dt2,dt2 + dtx,dtx)
                dt2 = dt2 + dtx
            elif (dtx <= 0):
                dtx = -dtx
                servx = np.arange(dt2 - dtx,dt2,dtx)
                dt2 = dt2 - dtx
            if (dty >= 0):
                servy = np.arange(dt1,dt1 + dty,dty)
                dt1 = dt1 + dty
            elif (dty <= 0):
                dty = -dty
                servy = np.arange(dt1 - dty,dt1,dty)
                dt1 = dt1 - dty
            #################    
            if (dt1 <= 2.5):
                dt1 = 2.5
            elif (dt1 >= 11):
                dt1 = 11
            if (dt2 <= 2.5):
                dt2 = 2.5
            elif (dt2 >= 11):
                dt2 = 11
            ################# 
            for f in servx:
                pwm2.ChangeDutyCycle(f)
                sleep(timex)
            for u in servy:
                pwm1.ChangeDutyCycle(u)
                sleep(timey)
            ################# 
            xposservo = (int(f*10)/1)
            xposservo = (int(u*10)/1)
##############################
    except Exception as excerr:
        print("nothin found")
        print(excerr)
        if ("name 'notfound' is not defined" == str(excerr)):
            print("nothing found")
            dt2 = dt2 + 1
            if (dt2 >= 11):
                dt2 = 2
                dt1 = dt1 + 0.5
                if (dt1 >= 6):
                        dt1 = 2
            pwm1.ChangeDutyCycle((int(dt1*10)/10))
            pwm2.ChangeDutyCycle((int(dt2*10)/10))
        elif("float division by zero" == str(excerr)):
            print("servostop")
###############################################################
    cv.imshow('window', hilight)
    cv.imshow('frame', frame)
###############################################################
    ikey = cv.waitKey(5)
    if (ikey==ord("q")):
        cv.destroyAllWindows()
        pwm1.stop()
        pwm2.stop()
        rp.cleanup()
        vs.stop()
        break
