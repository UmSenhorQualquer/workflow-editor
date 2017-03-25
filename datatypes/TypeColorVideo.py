import cv2, math
#This class is a module that indicate that the input is of video type

class TypeColorVideo(object):

	def __init__(self): 
		self._currentImage 		= None
		self._capture 			= None
		self._captureFromFile 	= None

	def open(self, captureFrom = None):
		if captureFrom: 
			self._capture = cv2.VideoCapture( captureFrom )
			self._captureFromFile = captureFrom
	def release(self):
		if self._capture: self._capture.release()

	def get(self, flag): 		return self._capture.get( flag )
	def set(self, flag, value): return self._capture.set( flag, value )

	def read(self, tick=None):
		res, image  = self._capture.read()
		self._currentImage = image = self.processFrame(image)
		return res, image

	def processFrame(self, image): return image

	def isReady(self): return self._capture!=None

	@property
	def currentImage(self): return self._currentImage