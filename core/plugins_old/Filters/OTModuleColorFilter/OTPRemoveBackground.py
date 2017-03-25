import cv2, time, itertools
from numpy import *
from math import *

from core.controllers.OTPBase import *


class OTPRemoveBackground(OTPBase):

    _param_background_threshold = 0
    
    def __init__(self, **kwargs):
    	super(OTPRemoveBackground, self).__init__(**kwargs)
        self._param_background_threshold = 0
        self._param_background = None  

    def compute(self, frame):
        if self._param_background==None:
            gray = self.subtract(frame,threshold=self._param_background_threshold, thresholdValue=1)
        else:
            gray = self._param_background._backgroundDetector.subtract(frame,threshold=self._param_background_threshold, thresholdValue=1)
        return gray

    def process(self, frame):
    	frame = super(OTPRemoveBackground, self).process(frame)
    	return OTPRemoveBackground.compute(self,frame)