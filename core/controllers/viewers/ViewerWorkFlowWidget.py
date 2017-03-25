from core.controllers.viewers.BaseViewer import BaseViewer
from core.modules.OTModuleWorkFlowItem import OTModuleWorkFlowItem
from core.modules.ModuleConnection import ModuleConnection
from PyQt4.Qt import QGLWidget
import OpenGL.GL  as GL
import OpenGL.GLU as GLU


class ViewerWorkFlowWidget(QGLWidget, BaseViewer):
	"""
	Class that implements the Work flow graphical perspectives of the current project
	"""
	

	def __init__(self, parentController=None):
		BaseViewer.__init__(self, parentController)
		QGLWidget.__init__(self, parentController.form)
		self.setMouseTracking(True)
		self.setAcceptDrops(True)

		self._nodes             = {}
		self._nodesConnections  = []
		self._modulesList       = []

		self._zoom      = 0.4
		self._mouseX    = 0.0
		self._mouseY    = 0.0
		self._glX       = 0.0
		self._glY       = 0.0
		self._glZ       = 0.0
		self._width     = 1.0
		self._height    = 1.0
		self._x         = 0.0
		self._y         = 0.0
		self._lastGlX   = 0.0
		self._lastGlY   = 0.0
		self._moveGlX   = 0.0
		self._moveGlY   = 0.0
		self._mouseDown = False

		self.setMinimumHeight(200)

		self._nodes = {}
		self._nodesConnections = []
		self._modulesList = []

		self._selectedObject = None


	def dragEnterEvent(self, e):
		shouldAccept = False

		if  e.source()==self._controller.pluginsTree and \
			e.format()=='application/x-qabstractitemmodeldatalist':
			
			for item in e.source().selectedItems():
				if not hasattr(item, 'pluginfile'): 
					shouldAccept=False
					break
				else:
					shouldAccept=True

		if shouldAccept: e.accept()
		else:e.ignore()

	def dropEvent(self, e):
		pos = e.pos()
		self._mouseX = pos.x()
		self._mouseY = pos.y()
		self.repaint()
		for item in e.source().selectedItems():
			self._controller.addModule2Project(item, (self._glX, self._glY) )
		

	def saveContent(self, saver):
		"""
		BaseViewer.saveContent reimplementation
		"""
		BaseViewer.saveContent(self, saver)

		saver['_zoom'] = self._zoom
		saver['_x'] = self._x
		saver['_y'] = self._y
		saver['_lastGlX'] = self._lastGlX
		saver['_lastGlY'] = self._lastGlY


	def loadSavedContent(self, loader):
		"""
		BaseViewer.loadSavedContent reimplementation
		"""
		BaseViewer.loadSavedContent(self, loader)

		try:
			self._zoom = loader['_zoom']
			self._x = loader['_x']
			self._y = loader['_y']
			self._lastGlX = loader['_lastGlX']
			self._lastGlY = loader['_lastGlY']
		except Exception as e:
			print "Error: BaseViewerWorkFlowWidget: ", str(e)
		

	def initializeGL(self):
		GL.glClearDepth(1.0)
		GL.glClearColor(0, 0, 0, 1.0)
		GL.glShadeModel(GL.GL_SMOOTH)
		GL.glEnable(GL.GL_DEPTH_TEST)
		GL.glEnable(GL.GL_LIGHTING)
		GL.glEnable(GL.GL_LIGHT0)
		GL.glEnable(GL.GL_COLOR_MATERIAL)

		
		GL.glEnable(GL.GL_LINE_SMOOTH);
		GL.glEnable(GL.GL_POLYGON_SMOOTH)
		GL.glHint(GL.GL_POLYGON_SMOOTH_HINT, GL.GL_NICEST)
	   
	def resizeGL(self, width, height):
		GL.glViewport(0, 0, width, height)
		GL.glMatrixMode(GL.GL_PROJECTION)
		GL.glLoadIdentity()
		GLU.gluPerspective(40.0, float(width) / float(height), 0.01, 10.0)

	def paintGL(self):
		GL.glClearColor(1, 1, 1, 1.0)
		GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
		GL.glMatrixMode(GL.GL_MODELVIEW)
		GL.glLoadIdentity()

		GL.glTranslatef(0, 0, -self._zoom)


		GL.glColor4f(1, 1, 1, 1.0)
		GL.glBegin(GL.GL_QUADS)
		GL.glVertex3f(20, -20, 0)
		GL.glVertex3f(20, 20, 0)
		GL.glVertex3f(-20, 20, 0)
		GL.glVertex3f(-20, -20, 0)
		GL.glEnd()

		modelview = GL.glGetDoublev(GL.GL_MODELVIEW_MATRIX)
		projection = GL.glGetDoublev(GL.GL_PROJECTION_MATRIX)
		viewport = GL.glGetIntegerv(GL.GL_VIEWPORT)
		winX = float(self._mouseX);
		winY = float(viewport[3] - self._mouseY)
		winZ = GL.glReadPixels(winX, winY, 1, 1, GL.GL_DEPTH_COMPONENT, GL.GL_FLOAT)
		self._glX, self._glY, self._glZ = GLU.gluUnProject(winX, winY, winZ[0][0], modelview, projection, viewport)
		
		####CLEAR EVERYTHING
		GL.glClearColor(1, 1, 1, 1.0)
		GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)
		GL.glMatrixMode(GL.GL_MODELVIEW)
		GL.glLoadIdentity()
		
		GL.glTranslatef(0, 0, -self._zoom)

		GL.glEnable(GL.GL_LIGHTING)
		GL.glEnable(GL.GL_LIGHT0)
		GL.glEnable(GL.GL_COLOR_MATERIAL)

		GL.glTranslatef(self._x - self._moveGlX, self._y - self._moveGlY, 0.0)

		
		for node in self._nodes.values(): 
			node.viewerDraw()
			GL.glColor4f( 0.0, 0.0, 0.0, 1.0)
			self.renderText(    node._viewer_x+node._viewer_radius+0.005,
								node._viewer_y-0.001,
								0.0, node.name)

		for module in self._nodes.values():
			for name, param  in module.controls.items():
				connectedModule = param.value
				if isinstance(param, ModuleConnection) and isinstance( connectedModule, OTModuleWorkFlowItem):
					connectedModule.viewerDrawConnectionBetween(module)
	
		GL.glDisable(GL.GL_LIGHTING)
		GL.glDisable(GL.GL_LIGHT0)
		GL.glDisable(GL.GL_COLOR_MATERIAL)
		

	def selectItem(self, x, y, z):
		for node in self._nodes.values():
			if node.checkPointCollision(x, y, z):
				return node
		return None


	#Mouse EVENTS
	def wheelEvent(self, event):
		if event.delta() < 0: self._zoom += 0.1
		else: self._zoom -= 0.1
		if self._zoom < 0.01: self._zoom = 0.02
		self.repaint()

	def mouseReleaseEvent(self, event):

		if event.button() == 2:
			self._mouseDown = False
			self._x -= self._moveGlX
			self._y -= self._moveGlY
			self._moveGlX = 0.0
			self._moveGlY = 0.0

		if event.button() == 1:
			if self._selectedObject:
				self._selectedObject.viewerDeselect()
				self._selectedObject = None
				self.repaint()



	def mousePressEvent(self, event):
		QGLWidget.mousePressEvent(self, event)

		if event.button() == 1 or event.button() == 2:
			self._mouseX = event.x()
			self._mouseY = event.y()
			self.repaint()
			self._lastGlX = self._glX
			self._lastGlY = self._glY

		if event.button() == 2:
			self._mouseDown = True
			self.repaint()

		if event.button() == 1:
			self._selectedObject = self.selectItem(self._glX-self._x, self._glY-self._y, self._glZ)
			if self._selectedObject:
				self._selectedObject.viewerSelect()
				self.repaint()

	def mouseMoveEvent(self, event):
		if self._mouseDown or self._selectedObject:
			self._mouseX = event.x()
			self._mouseY = event.y()
			self.repaint()

		if self._mouseDown:
			self._moveGlX = self._lastGlX - self._glX
			self._moveGlY = self._lastGlY - self._glY

		if self._selectedObject:
			self._selectedObject.viewerMoveTo(self._glX-self._x, self._glY-self._y, self._glZ)
			self.repaint()
			
	
	def mouseDoubleClickEvent(self, event):
		self._mouseX = event.x()
		self._mouseY = event.y()
		self.repaint()
		self._selectedObject = self.selectItem(self._glX-self._x, self._glY-self._y, self._glZ)
		if self._selectedObject:
			self._selectedObject.show()
			self._selectedObject = None
			#self._controller.form.tabWidget.setCurrentIndex(0)
	

	def updateView(self, project):
		"""Update the view"""
		BaseViewer.updateView(self, project)

		if project==None:
			self._modulesList = []
			self._nodesConnections = []
			self._nodes = {}
			self._selectedObject = None
		else:
			self._modulesList = []
			self._nodes = {}

			for module in self._project.modulesOrdered:
				if isinstance(module, OTModuleWorkFlowItem) and module not in self._modulesList:
					self._modulesList.append(module)
					self._nodes[module.uid] = module

			self._nodesConnections = []
			for module in self._modulesList:
				for name, param  in module.controls.items():
					connectedModule = param.value
					if isinstance(param, ModuleConnection) and isinstance( connectedModule, OTModuleWorkFlowItem):
						self._nodesConnections.append( (module.uid, connectedModule.uid) )

		self.repaint()

	@property
	def form(self): return self
	