import cv2, time, itertools
from numpy import *
from math import *

from core.controllers.OTPBase import *

def biggestContour(contours):
    biggest = None
    biggerArea = 0
    for blob in contours:
        area = cv2.contourArea(blob)
        if area>biggerArea:
            biggerArea = area
            biggest = blob
    return biggest



class OTPThreshBlobs(OTPBase):

    _param_tb_color_component = 0
    _param_tb_color_domain = 1000
    _param_tb_adaptive_method = 0
    _param_tb_box_height = 0
    _param_tb_box_width = 0
    _param_tb_block_size = 0
    _param_tb_c = 0
    
    def __init__(self, **kwargs):
        super(OTPThreshBlobs, self).__init__(**kwargs)
        self._param_tb_color_component = 0
        self._param_tb_color_domain = 1000
        self._param_tb_adaptive_method = 0
        self._param_tb_box_height = 0
        self._param_tb_box_width = 0
        self._param_tb_block_size = 0
        self._param_tb_c = 0


    def compute(self, blobs):
        
        if (self._param_tb_block_size % 2)==0: self._param_tb_block_size += 1

        for blob in blobs:
            p1, p2 = blob._bounding
            p1 = p1[0]-self._param_tb_box_width, p1[1]-self._param_tb_box_height
            p2 = p2[0]+self._param_tb_box_width, p2[1]+self._param_tb_box_height
            image = self._original_frame[p1[1]:p2[1], p1[0]:p2[0]]

            if self._param_tb_color_domain>=0: 
                thresh = cv2.cvtColor( image , self._param_tb_color_domain)
            else:
                thresh = image

            if self._param_tb_color_domain!=cv2.COLOR_BGR2GRAY:
                colors = cv2.split(thresh)
                thresh = colors[self._param_tb_color_component]

            blob._tb_thresh_img = cv2.adaptiveThreshold(thresh,255,self._param_tb_adaptive_method,cv2.THRESH_BINARY_INV, self._param_tb_block_size, self._param_tb_c-255)

            blob._tb_thresh_img[0:3] = 0
            blob._tb_thresh_img[-4:-1] = 0
            blob._tb_thresh_img[:, 0:3] = 0
            blob._tb_thresh_img[:, -4:-1] = 0

            blobs_found, dummy = cv2.findContours(blob._tb_thresh_img.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE )
            biggest = biggestContour(blobs_found)

            blob._tb_biggest_img = zeros_like(blob._tb_thresh_img);  
            cv2.fillPoly(blob._tb_biggest_img, array([biggest]), (255,255,255))

            blob._tb_cut_bounding = p1, p2


            m = cv2.moments(biggest); m00 = m['m00']
            if m00!=0: centroid = ( int(round(m['m10']/m00) ), int(round(m['m01']/m00)) )
            else: centroid = (0,0)
            blob._contour = array( map( lambda p: [[p[0][0]+p1[0], p[0][1]+p1[1]]], biggest ) )
            box = cv2.boundingRect(blob._contour)
            blob._bounding = (box[0], box[1]), (box[0]+box[2], box[1]+box[3])
            blob._area = m00
            blob._centroid = centroid

        return blobs

    def process(self, blobs):
        blobs = super(OTPThreshBlobs, self).process(blobs)
        return OTPThreshBlobs.compute(self,blobs)