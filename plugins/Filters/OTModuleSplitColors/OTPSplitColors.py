import cv2, time, itertools
from numpy import *
from math import *

class OTPSplitColors(object):

    def __init__(self, **kwargs):
        #super(OTPSplitColors, self).__init__(**kwargs)
        self._split_color_channel = 0
        
    def compute(self, frame): return cv2.split(frame)[self._split_color_channel]

    def process(self, value):
        value = super(OTPSplitColors, self).process(value)
        return OTPSplitColors.compute(self,value)