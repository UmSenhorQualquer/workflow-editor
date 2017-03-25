import cv2, time, itertools
from numpy import *
from math import *

from core.controllers.OTPBase import *

class OTPAdaptativeThreshold(OTPBase):

    _param_tb_color_component = 0
    _param_tb_color_domain = 1000
    _param_tb_adaptive_method = 0
    _param_tb_block_size = 0
    _param_tb_c = 0
    _param_tb_threshold_type = 0
    
    def __init__(self, **kwargs):
        super(OTPAdaptativeThreshold, self).__init__(**kwargs)
        self._param_tb_color_component = 0
        self._param_tb_color_domain = cv2.COLOR_BGR2GRAY
        self._param_tb_adaptive_method = cv2.cv.CV_ADAPTIVE_THRESH_MEAN_C
        self._param_tb_threshold_type = cv2.THRESH_BINARY
        self._param_tb_block_size = 3
        self._param_tb_c = 255


    def compute(self, frame):
        
        if (self._param_tb_block_size % 2)==0: self._param_tb_block_size += 1

        if self._param_tb_color_domain>=0: 
            thresh = cv2.cvtColor( frame , self._param_tb_color_domain)
        else:
            thresh = frame

        if self._param_tb_color_domain!=cv2.COLOR_BGR2GRAY:
            colors = cv2.split(thresh)
            thresh = colors[self._param_tb_color_component]
        return cv2.adaptiveThreshold(thresh,255,self._param_tb_adaptive_method,self._param_tb_threshold_type, self._param_tb_block_size, self._param_tb_c-255)

    def process(self, image):
        self._out_original_image = image
        value = super(OTPAdaptativeThreshold, self).process(image)
        if isinstance(value, list):
            for blob in blobs: blob._image = OTPAdaptativeThreshold.compute(self, blob._image)
            return blobs
        else:
            return OTPAdaptativeThreshold.compute(self,value)