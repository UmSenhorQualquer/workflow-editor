import cv2, time, itertools
from numpy import *
from math import *

from core.controllers.OTPBase import OTPBase


class Blob(object): 


    def draw(self, frame):
        cv2.polylines(frame, array( [self._contour] ), True, (255,255,0), 2)


class OTPFindBlobs(OTPBase):

    _param_min_area = 0
    _param_max_area = 1000
    
    def __init__(self, **kwargs):
        super(OTPFindBlobs, self).__init__(**kwargs)
        self._param_min_area = 0
        self._param_max_area = 1000

    def process(self, frame):
        frame = super(OTPFindBlobs, self).process(frame)
        contours, hierarchy = cv2.findContours(frame.copy(), cv2.cv.CV_RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        objectsFound = []
        for cnt in contours:
            m = cv2.moments(cnt); m00 = m['m00']
            
            if m00 > self._param_min_area and m00 < self._param_max_area:

                if m00!=0: centroid = ( int(round(m['m10']/m00) ), int(round(m['m01']/m00)) )
                else: centroid = (0,0)

                box = cv2.boundingRect(cnt)
                p1, p2 = (box[0], box[1]), (box[0]+box[2], box[1]+box[3])
        
                obj = Blob()
                obj._contour = cnt
                obj._bounding = (p1, p2)
                obj._area = m00
                obj._centroid = centroid
                
                objectsFound.append( obj )

        return objectsFound