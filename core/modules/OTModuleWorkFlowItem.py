from core.modules.OTModuleProjectItem import OTModuleProjectItem
import cv2
import OpenGL.GL  as GL
import OpenGL.GLU as GLU
import math
import core.utils.tools as tools


class OTModuleWorkFlowItem(OTModuleProjectItem):
	"""
	Abstract class that implement the OTProjectViewerWorkFlowWidget item
	"""
	
	def __init__(self, name, *args, **keys):
		super(OTModuleWorkFlowItem, self).__init__(name,*args, **keys)

		self._iconTexture 		= None    			#: Opengl texture
		self._iconTextureFile 	= keys['iconFile'] 	#: Texture file
		self._viewer_x 		= 0.0 				#: X coord of the module in the viewer
		self._viewer_y 		= 0.0 				#: Y coord of the module in the viewer
		self._viewer_radius = 0.03 				#: Radius of the square icon in the viewer
		self._viewer_color 	= ( 1.0, 1.0, 1.0 ) #: Corlor of the module in viewer

	############################################################################
	############ Work flow item functions  #####################################
	############################################################################

	def viewerDraw(self):
		"""Function called to draw module in Workflow viewer"""
		if self._iconTexture == None: self._iconTexture = tools.LoadOpenGLTexture(self._iconTextureFile)

		GL.glPushMatrix()
		GL.glTranslatef(self._viewer_x, self._viewer_y, 0.0)
		GL.glColor4f(self._viewer_color[0],self._viewer_color[1],self._viewer_color[2], 1.0)
		GL.glBindTexture(GL.GL_TEXTURE_2D, self._iconTexture)
		GL.glEnable(GL.GL_TEXTURE_2D)
		
		tools.drawGLCircle(self._viewer_radius)
		
		GL.glDisable(GL.GL_TEXTURE_2D)
		GL.glPopMatrix()

	def viewerDrawConnectionBetween(self, module):
		"""
		Function called to draw the connections between modules in the Workflow viewer
		@param module: Module that "self" should connect
		@type module: OTModuleWorkFlowItem
		"""
		GL.glPushMatrix()
		GL.glEnable(GL.GL_BLEND);
		GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
		
		#Draw arrow
		v_x = (self._viewer_x - module._viewer_x)
		v_y = (self._viewer_y - module._viewer_y)
		angle = math.atan2(v_y, v_x)
		radius = 0.02
		GL.glColor4f(0.0,0.0,1.0, 0.2)
		GL.glLineWidth (3.0)
		pointX = module._viewer_x + math.cos(angle)*self._viewer_radius
		pointY = module._viewer_y + math.sin(angle)*self._viewer_radius
		x = pointX + math.cos(angle+(math.pi/5.0))*radius
		y = pointY + math.sin(angle+(math.pi/5.0))*radius
		GL.glBegin(GL.GL_LINES)
		GL.glVertex3f( x, y ,  0.001)
		GL.glVertex3f( pointX, pointY, 0.001)
		GL.glEnd()
		x = pointX + math.cos(angle-(math.pi/5.0))*radius
		y = pointY + math.sin(angle-(math.pi/5.0))*radius
		GL.glBegin(GL.GL_LINES)
		GL.glVertex3f( x, y ,  0.001)
		GL.glVertex3f( pointX, pointY, 0.001)
		GL.glEnd()
		#Draw line
		GL.glLineWidth (5.0)
		GL.glBegin(GL.GL_LINES)
		GL.glColor4f( 1.0, 1.0, 1.0, 1.0)
		GL.glVertex3f( self._viewer_x, self._viewer_y,  -0.001)
		GL.glColor4f(0.0,0.0,1.0, .2)
		GL.glVertex3f( pointX, pointY, 0.001)
		GL.glEnd()
		GL.glLineWidth (1.0)
		GL.glPopMatrix()

	def viewerSelect(self):
		"""Enable the selection effect in the Workflow viewer"""
		self._viewer_color = (1.0, 1.0, 0.0)

	def viewerDeselect(self):
		"""Disable the selection effect in the Workflow viewer"""
		self._viewer_color = ( 1.0, 1.0, 1.0 )

	def viewerMoveTo(self, x, y, z):
		"""
		Move the module in the Workflow viewer
		@param x: X Opengl coordinate
		@type x: float
		@param y: Y Opengl coordinate
		@type y: float
		@param z: Z Opengl coordinate
		@type z: float
		"""
		diameter = self._viewer_radius*2
		self._viewer_x = round(x/diameter)*diameter
		self._viewer_y = round(y/diameter)*diameter

	def checkPointCollision(self, x, y, z):
		"""
		Check colision with a point x,y,z
		@param x: X Opengl coordinate
		@type x: float
		@param y: Y Opengl coordinate
		@type y: float
		@param z: Z Opengl coordinate
		@type z: float
		"""
		return math.hypot(self._viewer_x - x, self._viewer_y - y ) <= self._viewer_radius

	############################################################################
	############ Parent class functions reemplementation #######################
	############################################################################

	def save(self, saver):
		"""
		OTModule.saveContent reimplementation
		"""
		super(OTModuleWorkFlowItem, self).save(saver)
		saver['_viewer_color'] = self._viewer_color
		saver['_viewer_x'] = self._viewer_x
		saver['_viewer_y'] = self._viewer_y

	def load(self, loader):
		"""
		OTModule.loadSavedContent reimplementation
		"""
		super(OTModuleWorkFlowItem, self).load(loader)
		if '_viewer_color' in loader: self._viewer_color = loader['_viewer_color']
		if '_viewer_x' in loader: self._viewer_x = loader['_viewer_x']
		if '_viewer_y' in loader: self._viewer_y = loader['_viewer_y']

	@property
	def position(self): return self._viewer_x, self._viewer_y
	@position.setter
	def position(self, value):
		self._viewer_x, self._viewer_y = value