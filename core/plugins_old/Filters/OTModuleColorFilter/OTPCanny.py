import cv2, time, itertools
from numpy import *
from math import *

from core.controllers.OTPBase import *

class OTPCanny(OTPBase):

    _param_canny_apertureSize = 0
    _param_canny_L2gradient = 0
    _param_canny_threshould1 = 0
    _param_canny_threshould2 = 0
    _param_canny_color_domain = 0
    _param_canny_color_component = 0

    def __init__(self, **kwargs):
    	super(OTPCanny, self).__init__(**kwargs)
        self._param_canny_apertureSize = 3
        self._param_canny_L2gradient = True
        self._param_canny_threshould1 = 0
        self._param_canny_threshould2 = 1

        self._param_canny_color_domain = cv2.COLOR_BGR2GRAY
        self._param_canny_color_component = 0

    def compute(self, frame):
        if (self._param_canny_apertureSize % 2)==0: self._param_canny_apertureSize += 1

        if self._param_canny_color_component>=0: 
            thresh = cv2.cvtColor( frame , self._param_canny_color_component)
        else:
            thresh = frame

        if self._param_canny_color_domain!=cv2.COLOR_BGR2GRAY:
            colors = cv2.split(thresh)
            thresh = colors[self._param_canny_color_component]

        return cv2.Canny( thresh, self._param_canny_threshould1, self._param_canny_threshould2, apertureSize=self._param_canny_apertureSize, L2gradient=self._param_canny_L2gradient )
       
    def process(self, frame):
        self._out_original_image = frame
    	value = super(OTPCanny, self).process(value)
        if isinstance(value, list):
            for blob in blobs: blob._image = OTPCanny.compute(self, blob._image)
            return blobs
        else:
            return OTPCanny.compute(self,value)