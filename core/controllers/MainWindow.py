import sys, os, glob
from PyQt4.QtCore import *
from PyQt4 import uic, QtGui
import core.utils.tools as tools


from core.modules.OTModuleProject import OTModuleProject
from core.controllers.viewers.ViewerModulesListWidget import ViewerModulesListWidget
from core.controllers.viewers.ViewerWorkFlowWidget import ViewerWorkFlowWidget
from core.controllers.AvailablePluginsTree import AvailablePluginsTree


from pyforms 			import BaseWidget
from pyforms.Controls 	import ControlDockWidget
from pyforms.Controls 	import ControlTree
from pyforms.Controls 	import ControlOpenGL
from pyforms.Controls 	import ControlMdiArea
from pyforms.Controls 	import ControlEmptyWidget

class MainWindow(BaseWidget):
	"""
	This class implement the Main Window user interface.
	"""

	_rootModule = None              #: Active project
	_form = None                    #: Qt user interface class
	_datasetsWindow = None          #: Qt user interface data sets window
	

	_loadedModulesClasses={}


	def __init__(self):
		super(MainWindow, self).__init__('Workflow')

		self._leftDock  = ControlDockWidget('Project', side='left')
		self._rightDock = ControlDockWidget('Available Plugins', side='right')
		self._topDock = ControlDockWidget('Workflow', side='top')

		self._loadedPlugins = ViewerModulesListWidget()
		self.pluginsTree 	= AvailablePluginsTree(self)
		self._projWorkFlow  = ViewerWorkFlowWidget(self)
		self.mdiArea 		= ControlMdiArea('Windows')

		self._rightDock.value = self.pluginsTree
		self._leftDock.value  = self._loadedPlugins
		self._topDock.value   = self._projWorkFlow

		
		
		#self._projWorkFlow 	= ControlOpenGL('Project Workflow')
		
		

		self._formset 		= ['mdiArea']


		self.mainmenu = [
			{ 'File': [
					{'New':  self.__newProjectEvent  },
					{'Open': self.__openProjectEvent },
					'-',
					{'Save': self.__saveProjectEvent },
					'-',
					{'Close': self.__closeEvent },
				]
			}
		]

		self.pluginsTree.expandAll()
		self._viewers = [] #: Project viewers list
		self._viewers.append( self._loadedPlugins )
		self._viewers.append( self._projWorkFlow )

		#self.__newProject('projects')
		#data = self.openProject('projects/test', "project.ot")
		
		
	############################################################################
	############ Interface events ##############################################
	############################################################################

	
	def __newProject(self, projectDir):
		path, folderName = os.path.split( projectDir )
		self._rootModule = OTModuleProject(self, folderName, projectDir)
		self._rootModule.moduleUpdatedEvent = self.updateViewers
		self._rootModule.addModuleEvent 	= self.__addModuleEvent
	
	def __newProjectEvent(self):
		"""
		Menu File >> New >> Project type - trigger event implementation
		@param directory: Project type directory
		@type directory: String
		@param file: Project type file name
		@type file: String
		"""
		self.closeProject()

		projectDir = QtGui.QFileDialog.getExistingDirectory(self.form, 'Select project folder', 'projects')
		if projectDir:
			self.__newProject(str(projectDir))


	def __openProjectEvent(self):
		"""
		Menu File >> Open - trigger event implementation
		@param position: Point in the window where the menu will be shown
		@type position: QPoint
		"""
		projectDir = QtGui.QFileDialog.getExistingDirectory(self.form, 'Select project folder', 'projects')
		if projectDir: 
			data = self.openProject(projectDir, "project.ot")

			


	def __saveProjectEvent(self):
		"""
		Menu File >> Save - trigger event implementation
		"""
		data = {}
		for viewer in self._viewers: viewer.saveContent(data)
		self._rootModule.saveProject( data )
		QtGui.QMessageBox.information(self.form, "Success", "Project saved with success!")



	def __closeEvent(self, event):
		"""
		Controller close event
		@param event: event object
		@type event: QCloseEvent
		"""
		if self._rootModule: self._rootModule.close()

	############################################################################
	############ Other functions ###############################################
	############################################################################
			

	def closeProject(self):
		if self._rootModule: self._rootModule.close()
		self._rootModule = None
		self.updateViewers(self._rootModule)

	def updateViewers(self, project):
		"""
		Update viewers interface
		@param project: Project class
		@type project: OTModuleProject
		"""
		for viewer in self._viewers: viewer.updateView( project )
		
	def openProject(self, projectDir, file):
		"""
		Open a project
		@param directory: Project type directory
		@type directory: String
		@param file: Project type file name
		@type file: String
		"""
		self.closeProject()
		
		self._rootModule 					= OTModuleProject(self)
		self._rootModule.moduleUpdatedEvent = self.updateViewers
		self._rootModule.addModuleEvent 	= self.__addModuleEvent
			
		data = self._rootModule.openProject( projectDir, file )

		if data!=None:
			for viewer in self._viewers: viewer.loadSavedContent(data)
		self.updateViewers(self._rootModule)

		return data
	

	
	def addModule2Project(self, modulesTreeItem, pos=(0,0)):
		if self._rootModule is None:
			QtGui.QMessageBox.critical(None, "Project is not loaded", "Please create or open a project first!")
			return

		moduleclassname = modulesTreeItem.pluginclass
		modulepath 		= modulesTreeItem.pluginfile

		moduleclass 	= None
		if moduleclassname in self._loadedModulesClasses:
			moduleclass = self._loadedModulesClasses[moduleclassname]
		else:
			tmp = modulepath.split(os.path.sep)
			m = ".".join(tmp)+"."+moduleclassname
			moduleclass = __import__(m, fromlist=[moduleclassname])
			moduleclass =  getattr(moduleclass, moduleclassname)
			self._loadedModulesClasses[moduleclassname] = moduleclass

		module = moduleclass(moduleclassname)
		module.position = pos

		self._rootModule += module
		
		
		

	def __addModuleEvent(self, module):
		"""
		Add module to the current project
		@param module: Module to add
		@type module: OTModule
		"""
		self.mdiArea += module
		

	############################################################################
	############ Properties ####################################################
	############################################################################

