import cv2, time, itertools
from numpy import *
from math import *

from core.controllers.OTPBase import *


class Blob(object): 


    def draw(self, frame): cv2.polylines(frame, array( [self._contour] ), True, (255,255,0), 2)

    def distanceTo(self, blob):
        p0 = self._centroid
        p1 = blob._centroid
        return math.sqrt((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2)

    def angleBetween(self, previous_blob, next_blob):
        if isinstance( previous_blob, tuple ) and isinstance( next_blob, tuple ):
            pt0, pt1, pt2 = previous_blob, self._centroid, next_blob
        else:
            pt0, pt1, pt2 = previous_blob._centroid, self._centroid, next_blob._centroid
        dx1 = pt0[0] - pt1[0]
        dy1 = pt0[1] - pt1[1]
        dx2 = pt2[0] - pt1[0]
        dy2 = pt2[1] - pt1[1]
        nom = dx1*dx2 + dy1*dy2
        denom = math.sqrt( (dx1*dx1 + dy1*dy1) * (dx2*dx2 + dy2*dy2) + 1e-10 )
        ang = nom / denom
        return math.degrees( math.acos(ang) )




class OTPFindBlobs(OTPBase):

    _param_min_area = 0
    _param_max_area = 100000000
    
    def __init__(self, **kwargs):
        super(OTPFindBlobs, self).__init__(**kwargs)
        self._param_min_area = 0
        self._param_max_area = 100000000

    def compute(self, frame):
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

    def process(self, frame):
        frame = super(OTPFindBlobs, self).process(frame)
        return OTPFindBlobs.compute(self,frame)