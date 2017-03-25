import cv2, time, itertools
from numpy import *
from math import *

from core.controllers.OTPBase import *

class OTPBlur(OTPBase):

    _param_kernel_size = 3
    _param_blur_threshould = 0

    def __init__(self, **kwargs):
    	super(OTPBlur, self).__init__(**kwargs)
        self._param_kernel_size = 3
        self._param_blur_threshould = 0

    def compute(self, frame):
        frame = cv2.blur( frame, (self._param_kernel_size, self._param_kernel_size) )
        ret, frame = cv2.threshold(frame, self._param_blur_threshould, 255, cv2.THRESH_BINARY) 
        return frame

    def process(self, frame):
    	frame = super(OTPBlur, self).process(frame)
        return OTPBlur.compute(self, frame)