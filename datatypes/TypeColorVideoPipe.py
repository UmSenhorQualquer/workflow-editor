from TypeColorVideo import TypeColorVideo
import cv2
#This class is a module that indicate that the input is of video type

class TypeColorVideoPipe(TypeColorVideo):

	def __init__(self): 
		self._inputvideo = None
		TypeColorVideo.__init__(self)

	def open(self, inputvideo):
		if inputvideo: self._inputvideo = inputvideo
	def release(self): self._inputvideo.release()

	def get(self, flag):		return self._inputvideo.get( flag )
	def set(self, flag, value): return self._inputvideo.set( flag, value )

	def read(self): 
		res, image = self._inputvideo.read()
		image = self.processFrame(image)
		return res, image
	def processFrame(self, image): return frame

	def isReady(self): 
		if self._inputvideo==None: return False
		return self._inputvideo.isReady()