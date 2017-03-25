import cv2, time, itertools
from numpy import *
from math import *

from core.controllers.OTPBase import *

class OTPMaskImage(OTPBase):

    _param_mi_polygons = None
    _param_mi_mask = None

    def __init__(self, **kwargs):
        super(OTPMaskImage, self).__init__(**kwargs)
        self._param_mi_polygons = None
        self._param_mi_mask = None

    def compute(self, frame):
        if self._param_mi_mask==None:
            self._param_mi_mask = zeros( frame.shape, dtype=uint8 )
            for poly in self._param_mi_polygons: cv2.fillPoly( self._param_mi_mask, [array(poly,int32)], (255,255,255) )

        #return self._param_mi_mask 
        return cv2.bitwise_and(frame, self._param_mi_mask)

    def process(self, frame):
        frame = super(OTPMaskImage, self).process(frame)
        return OTPMaskImage.compute(self, frame)