from TypeColorVideo import TypeColorVideo
import cv2
#This class is a module that indicate that the input is of video type

class TypeSingleChannelImage(object):

    def __init__(self): 
        self._inputvideo = None
        

    def open(self, inputvideo):
        if inputvideo: self._inputvideo = inputvideo
    def release(self): self._inputvideo.release()

    def get(self, flag):        return self._inputvideo.get( flag )
    def set(self, flag, value): return self._inputvideo.set( flag, value )

    def read(self): 
        image = self._inputvideo.currentImage
        image = self.processFrame(image)
        return image!=None, image
    def processFrame(self, image): return frame

    def isReady(self): 
        if self._inputvideo==None: return False
        return self._inputvideo.isReady()