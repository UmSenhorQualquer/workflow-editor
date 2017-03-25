import sys; sys.path.append('../../../../')
import cv2
from core.controllers.OTPBase import OTPBase

class OTPOpenVideo(OTPBase):
	
	def __init__(self,**kwargs):
		super(OTPOpenVideo, self).__init__(**kwargs)

	def compute(self, filename):
		capture = cv2.VideoCapture(filename)
		res = True
		while res:
			res, image = capture.read()
			yield image 

	def process(self, filename):
		filename = super(OTPOpenVideo, self).process(filename)
		return OTPOpenVideo.compute(self,filename)


if __name__ == "__main__":

	proc = OTPOpenVideo()

	val = proc.process('/home/ricardo/Desktop/teste.avi')
	for x in val:
		print x
	
