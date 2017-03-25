import cv2
from numpy import *
from math import *


from core.controllers.OTPBase import *

class OTPBackGroundDetector(OTPBase):

	_background = None
	_background_color	= [None,None,None]
	_backgroundSum 		= [None,None,None]
	_backgroundAverage 	= [None,None,None]
	_backgroundCounter 	= [None,None,None]
	_gaussianBlurMatrixSize = None
	_gaussianBlursigmaX = None
	_capture = None
	_width = 0
	_height = 0
	_updateFunction = None

	_param_bgdetector_no_cache = True
	_param_bgdetector_threshold = 5
	_param_bgdetector_jump=30
	_param_bgdetector_compare_jump = 500

	
	def __init__(self,**kwargs):
		super(OTPBackGroundDetector, self).__init__(**kwargs)
		capture=None; gaussianBlurMatrixSize=3; gaussianBlursigmaX=5; updateFunction=None
		if "capture" not in kwargs.keys(): print "The variable capture was not set in the object constructer"; exit()
		else: capture = kwargs['capture']
		if "gaussianBlurMatrixSize" in kwargs.keys(): gaussianBlurMatrixSize = kwargs['gaussianBlurMatrixSize']
		if "gaussianBlursigmaX" in kwargs.keys(): gaussianBlursigmaX = kwargs['gaussianBlursigmaX']
		if "updateFunction" in kwargs.keys(): updateFunction = kwargs['updateFunction']

		self._width = capture.get( cv2.cv.CV_CAP_PROP_FRAME_WIDTH )
		self._height = capture.get( cv2.cv.CV_CAP_PROP_FRAME_HEIGHT )
		self._capture = capture
		self._gaussianBlurMatrixSize = gaussianBlurMatrixSize
		self._gaussianBlursigmaX = gaussianBlursigmaX
		self._updateFunction = updateFunction
		self.__initialize__()

	def compute(self, frame):
		if self._background==None:
			if not self._param_bgdetector_no_cache:
				self._background = cv2.imread("gray_background.png", 0)
				self._background_color = cv2.imread("color_background.png", 1)
			if self._background==None or self._background_color==None:
				self.detect( self._param_bgdetector_jump, self._param_bgdetector_compare_jump, self._param_bgdetector_threshold )
				cv2.imwrite("gray_background.png",self.background)
				cv2.imwrite( "color_background.png",self.background_color)
		return frame

	def process(self, frame):
		frame = super(OTPBackGroundDetector, self).process(frame)
		return OTPBackGroundDetector.compute(self, frame)

	def save( self, data ):
		data['_background'] = self._background
		data['_backgroundSum'] = self._backgroundSum
		data['_backgroundSum'] = self._backgroundAverage
		data['_backgroundCounter'] = self._backgroundCounter
		data['_gaussianBlurMatrixSize'] = self._gaussianBlurMatrixSize
		data['_gaussianBlursigmaX'] = self._gaussianBlursigmaX
		data['_width'] = self._width
		data['_height'] = self._height

	def load( self, data ):
		self._background = data['_background']
		self._backgroundSum = data['_backgroundSum']
		self._backgroundAverage = data['_backgroundSum'] 
		self._backgroundCounter = data['_backgroundCounter'] 
		self._gaussianBlurMatrixSize = data['_gaussianBlurMatrixSize'] 
		self._gaussianBlursigmaX = data['_gaussianBlursigmaX']
		self._width = data['_width'] 
		self._height = data['_height']

	def __initialize__(self):
		z = zeros( (self._height, self._width), float32 )
		self._backgroundSum = [z.copy(),z.copy(),z.copy()]
		self._backgroundCounter = [z.copy(),z.copy(),z.copy()]

	def cleanNoise(self, frame):
		"""
		originalYCrCb = cv2.cvtColor(frame, cv2.COLOR_BGR2YCR_CB)
		Y, Cr, Cb = cv2.split(originalYCrCb)
		Y  = cv2.GaussianBlur(Y,  (self._gaussianBlurMatrixSize, self._gaussianBlurMatrixSize), self._gaussianBlursigmaX)
		Cr = cv2.GaussianBlur(Cr, (self._gaussianBlurMatrixSize, self._gaussianBlurMatrixSize), self._gaussianBlursigmaX)
		Cb = cv2.GaussianBlur(Cb, (self._gaussianBlurMatrixSize, self._gaussianBlurMatrixSize), self._gaussianBlursigmaX)
		return Y, Cr, Cb
		"""
		return cv2.split(frame)

	def __process(self, frame, jump2Frame=2000, comprate2jumpFrame = 1000, threshold = 5 ):
		current_frame_index = self._capture.get( cv2.cv.CV_CAP_PROP_POS_FRAMES )
		Y, Cr, Cb = self.cleanNoise(frame)
		
		self._capture.set( cv2.cv.CV_CAP_PROP_POS_FRAMES, current_frame_index + comprate2jumpFrame )
		res, next_frame = self._capture.read()

		if self._updateFunction!=None: self._updateFunction( int(self._capture.get(cv2.cv.CV_CAP_PROP_POS_FRAMES)) )
		if res==False: return None
		Y_next, Cr_next, Cb_next = self.cleanNoise(next_frame)

		self._capture.set( cv2.cv.CV_CAP_PROP_POS_FRAMES, current_frame_index + jump2Frame )
		Y_diff, Cr_diff, Cb_diff = cv2.absdiff( Y, Y_next ), cv2.absdiff( Cr, Cr_next ), cv2.absdiff( Cb, Cb_next )
		
		ret , Y_gray = cv2.threshold(Y_diff, threshold , 255, cv2.THRESH_BINARY )
		ret , Cr_gray = cv2.threshold(Cr_diff, threshold , 255, cv2.THRESH_BINARY )
		ret , Cb_gray = cv2.threshold(Cb_diff, threshold , 255, cv2.THRESH_BINARY )

		contours, hierarchy = cv2.findContours(Y_gray, cv2.cv.CV_RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

		hulls = []
		for contour in contours: hulls.append( cv2.convexHull( contour ) )

		Y_backgroundArea = ones( (self._height, self._width), float32 )
		Cr_backgroundArea = Y_backgroundArea.copy()
		Cb_backgroundArea = Y_backgroundArea.copy()

		cv2.drawContours( Y_backgroundArea,  array( hulls ) , -1, (0), -1 )
		cv2.drawContours( Cr_backgroundArea, array( hulls ) , -1, (0), -1 )
		cv2.drawContours( Cb_backgroundArea, array( hulls ) , -1, (0), -1 )

		#if __name__ == "__main__": cv2.imshow("hulls", backgroundArea * 255)

		self._backgroundCounter[0] += Y_backgroundArea
		self._backgroundCounter[1] += Cr_backgroundArea
		self._backgroundCounter[2] += Cb_backgroundArea

		Y, Cr, Cb = cv2.split(frame)
		self._backgroundSum[0] += Y*Y_backgroundArea
		self._backgroundSum[1] += Cr*Cr_backgroundArea
		self._backgroundSum[2] += Cb*Cb_backgroundArea

		try:
			seterr(all ='ignore')
			self._backgroundAverage[0] = divide(self._backgroundSum[0] , self._backgroundCounter[0] )
			self._backgroundAverage[1] = divide(self._backgroundSum[1] , self._backgroundCounter[1] )
			self._backgroundAverage[2] = divide(self._backgroundSum[2] , self._backgroundCounter[2] )
		except:
			pass




	def detect(self, jump2Frame=0, comprate2jumpFrame = 1000, threshold = 5 ):

		self.__initialize__()
		self._capture.set( cv2.cv.CV_CAP_PROP_POS_FRAMES, 0 )
		res = True
		old_state = seterr(all ='ignore')
		while res:
			res, current_frame = self._capture.read()
			if not res: break
			self.__process(current_frame, jump2Frame, comprate2jumpFrame, threshold)

		self._background = cv2.convertScaleAbs(self._backgroundAverage[0])
		self._background_color = cv2.merge( (cv2.convertScaleAbs(self._backgroundAverage[0]), cv2.convertScaleAbs(self._backgroundAverage[1]), cv2.convertScaleAbs(self._backgroundAverage[2])))

		self._capture.set( cv2.cv.CV_CAP_PROP_POS_FRAMES, 0 )
		if self._updateFunction!=None: self._updateFunction( self._capture.get( cv2.cv.CV_CAP_PROP_FRAME_COUNT ) )
		seterr(**old_state)
		
		return self.background

	def quickDetect(self):
		self.detect(1000, 1500, 5)

	def subtract( self, frame, threshold=20, thresholdValue=255 ):
		diff = cv2.absdiff(frame , self._background_color)
		ret , res = cv2.threshold(diff, threshold , 255, cv2.THRESH_BINARY )
		diff = cv2.bitwise_and(frame, res)
		return diff

	@property
	def background(self): return self._background

	@property
	def background_color(self): return self._background_color











def ellipsePoint( ellipse, angle ):
	(center,axes,orientation) = ellipse
	x = center[0] + axes[0] * cos( angle ) * cos( orientation ) -  axes[1] * sin( angle ) * sin( orientation )
	y = center[1] + axes[0] * cos( angle ) * sin( orientation ) +  axes[1] * sin( angle ) * cos( orientation )
	return x, y


def pointsDistance(p1, p2):
    return  math.hypot(p2[0]-p1[0], p2[1]-p1[1])


def ellipsesClose2EachOther( ellipse1, ellipse2, maxDistance ):
	points2Test = 10.0

	countClose = 0.0

	step = 2 * pi / points2Test
	for angle_i in arange(0.0, 2*pi, step):
		for angle_j in arange(0.0, 2*pi, step):
			p1 = ellipsePoint(ellipse1, angle_i)
			p2 = ellipsePoint(ellipse2, angle_j)
			dist = pointsDistance(p1, p2)
			if dist<=maxDistance:
				countClose += 1
		#print p1, p2

	return countClose / (points2Test * points2Test) 


























if __name__ == "__main__":
	capture = cv2.VideoCapture("/home/ricardo/subversion/mouse_tracker/mouse_tracker_trunk/projects/new.avi")
	capture = cv2.VideoCapture("/home/ricardo/Desktop/exp004/arm preference/exp004_rats_11_12_22_9_ 12.avi")
	
	#capture = cv2.VideoCapture("/home/ricardo/subversion/mouse_tracker/mouse_tracker_trunk/projects/teste.avi")
	#capture = cv2.VideoCapture("/home/ricardo/NetBeansProjects/armarker/src/videos_new/1.mp4")
	#capture = cv2.VideoCapture("/media/MEMUP 320GB/KN047_120301.AVI")
	
	_gaussianBlurMatrixSize = 5
	_gaussianBlursigmaX = 5

	bg = BackGroundDetector(capture, _gaussianBlurMatrixSize, _gaussianBlursigmaX)

	#bg.detect( 100, 2000, 50 )
	#bg.detect(1000, threshold = 40)
	bg.quickDetect( )

	capture.set( cv2.cv.CV_CAP_PROP_POS_FRAMES, 0 )
	waitingTime = 1

	res = True
	while res:
		res, frame = capture.read()
		image = bg.cleanNoise(frame)
	
		diff = cv2.absdiff(image, bg.background)
		ret , gray = cv2.threshold(diff, 20 , 1, cv2.THRESH_BINARY )
		
		contours, hierarchy = cv2.findContours(gray.copy() * 255, cv2.cv.CV_RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
		
		hulls = []
		for contour in contours: 
			if len( contour )>=5:
				ellipse = cv2.fitEllipse(contour)
				
			hull = cv2.convexHull( contour )
			hulls.append(hull)
		
		gray3Channels = cv2.merge( (gray, gray, gray )) 
		cv2.imshow("Capture", frame * gray3Channels)


		key = cv2.waitKey(waitingTime)
		if key == ord('q'): exit()
		if key == ord('w'): waitingTime = 0
		if key == ord('e'): waitingTime = 1