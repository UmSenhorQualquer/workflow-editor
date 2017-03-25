import cv2, time, itertools
from numpy import *
from math import *

from core.controllers.OTPBase import *

class OTPConvertColor(OTPBase):

    def __init__(self, **kwargs):
        super(OTPConvertColor, self).__init__(**kwargs)
        self._param_color_domain = None
        
    def compute(self, frame):
        if self._param_color_domain>=0: 
            frame = cv2.cvtColor(frame, self._param_color_domain)
        return frame

    def process(self, value):
        
        value = super(OTPConvertColor, self).process(value)
        return OTPConvertColor.compute(self,value)