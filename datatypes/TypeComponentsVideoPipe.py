from TypeColorVideo import TypeColorVideo
import cv2
#This class is a module that indicate that the input is of video type

class TypeComponentsVideoPipe(TypeColorVideo):

	
	def __init__(self): 
		self._inputvideo=None
		TypeColorVideo.__init__(self)

	def open(self, inputvideo):
		if inputvideo: self._inputvideo = inputvideo

	def get(self, flag): return self._inputvideo.get( flag )

	def set(self, flag, value): return self._inputvideo.set( flag, value )

	def processFrame(self, image): return self.parentVideoInput.processFrame(image)

	def isReady(self): 
		if self._inputvideo==None: return False
		return self._inputvideo.isReady()

	def read(self): 
		res, image = self._inputvideo.read()
		image = self.processFrame(image)
		return res, image

	def getCurrentFrameImage(self): return self._inputvideo.getCurrentFrameImage()

	@property
	def parentVideoInput(self): return self._inputvideo
	@property
	def startFrame(self): return 0
	@property
	def endFrame(self): return self._inputvideo.endFrame

	@property
	def videoFrameTimeInterval(self): return self._inputvideo.videoFrameTimeInterval

	@property
	def fps(self): return self._inputvideo.fps

	@property
	def width(self): return  self._inputvideo.width
	@property
	def height(self): return self._inputvideo.height



	@property
	def currentFrameIndex(self): return self._inputvideo.currentFrameIndex

	@currentFrameIndex.setter
	def currentFrameIndex(self, value): self._inputvideo.currentFrameIndex = value

	def release(self): self._inputvideo.release()