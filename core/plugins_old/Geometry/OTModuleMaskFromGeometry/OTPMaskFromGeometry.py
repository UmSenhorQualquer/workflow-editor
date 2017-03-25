import cv2
import numpy as np
from core.controllers.OTPBase import OTPBase


class OTPMaskFromGeometry(OTPBase):

	_params_mask_contours = None

	_original_frame = None

	def __init__(self,**kwargs):
		super(OTPMaskFromGeometry, self).__init__(**kwargs)
		self._params_mask = None
		self._params_mask_contours = None
		self._original_frame = None

	def compute(self, frame):

		if self._params_mask==None:
			self._params_mask = np.zeros( frame.shape, dtype=np.uint8 )
			cv2.fillPoly( self._params_mask, self._params_mask_contours, (255,255,255) )
		return cv2.bitwise_and(frame, self._params_mask)

	def process(self, frame):
		frame = super(OTPMaskFromGeometry, self).process(frame)
		frame = OTPMaskFromGeometry.compute(self, frame)
		self._original_frame = frame.copy()		
		return frame

