import cv2, time, itertools
from numpy import *
from math import *

from core.controllers.OTPBase import *

class OTPAdaptativeThresholdFilter(OTPBase):

    
    def __init__(self, **kwargs):
        super(OTPAdaptativeThresholdFilter, self).__init__(**kwargs)
        self._param_tb_adaptive_method = cv2.cv.CV_ADAPTIVE_THRESH_MEAN_C
        self._param_tb_threshold_type = cv2.THRESH_BINARY
        self._param_tb_block_size = 3
        self._param_tb_c = 255

    def compute(self, frame):
        if (self._param_tb_block_size % 2)==0: self._param_tb_block_size += 1
        thresh = cv2.cvtColor(frame , cv2.COLOR_BGR2GRAY) if len(frame.shape)>2 else frame
        return cv2.adaptiveThreshold(thresh,255,self._param_tb_adaptive_method,self._param_tb_threshold_type, self._param_tb_block_size, self._param_tb_c-255)

    def process(self, image):
        value = super(OTPAdaptativeThresholdFilter, self).process(image)
        return OTPAdaptativeThresholdFilter.compute(self,value)