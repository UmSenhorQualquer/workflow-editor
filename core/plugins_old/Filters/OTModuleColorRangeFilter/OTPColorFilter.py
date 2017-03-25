import cv2, time, itertools
from numpy import *
from math import *

from core.controllers.OTPBase import *

class OTPColorFilter(OTPBase):

    _param_color_domain = None

    _param_a_min, _param_a_max = 0,255
    _param_b_min, _param_b_max = 0,255
    _param_c_min, _param_c_max = 0,255
    
    _param_filter_algorithm = None

    def __init__(self, **kwargs):
        super(OTPColorFilter, self).__init__(**kwargs)
        self._param_color_domain = None
        self._param_a_min, self._param_a_max = 0,255
        self._param_b_min, self._param_b_max = 0,255
        self._param_c_min, self._param_c_max = 0,255
        self._param_filter_algorithm = "A*B*C"

    def compute(self, frame):
        if self._param_color_domain>=0: work = cv2.cvtColor(frame, self._param_color_domain)
        else: work = frame

        A,B,C = cv2.split(work)

        A = cv2.inRange(A, array(self._param_a_min), array(self._param_a_max))
        B = cv2.inRange(B, array(self._param_b_min), array(self._param_b_max))
        C = cv2.inRange(C, array(self._param_c_min), array(self._param_c_max))
        ret, A = cv2.threshold(A, 0, 1, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        ret, B = cv2.threshold(B, 0, 1, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        ret, C = cv2.threshold(C, 0, 1, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        algo = self._param_filter_algorithm

        if len(algo)>0 and algo!='A*B*C':
            try:
                if "~A" in algo: 
                    not_A = cv2.absdiff(ones_like(A),A)
                    algo = algo.replace("~A", "not_A")
                if "~B" in algo: 
                    not_B = cv2.absdiff(ones_like(B),B)
                    algo = algo.replace("~B", "not_B")
                if "~C" in algo: 
                    not_C = cv2.absdiff(ones_like(C),C)
                    algo = algo.replace("~C", "not_C")
                frame = eval(algo)*255
            except:
                frame = A*B*C*255
        else:
            frame = A*B*C*255

        return frame

    def process(self, value):
        self._out_original_image = value
        value = super(OTPColorFilter, self).process(value)
        if isinstance(value, list):
            for blob in blobs: blob._image = OTPColorFilter.compute(self, blob._image)
            return blobs
        else:
            return OTPColorFilter.compute(self,value)