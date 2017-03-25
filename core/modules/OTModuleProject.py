from core.modules.OTModule import OTModule
from pyforms import BaseWidget
from PyQt4 import QtGui
from PyQt4 import QtCore

import plugins
import sys
import pickle
import os
import traceback

class OTModuleProject(OTModule):
	"""
	Implements the project management module
	"""
	_controller = None          #: modules controller
	_projectDir = None          #: Project dir
	_modules = {}               #: Dict of the project modules
	_modulesOrdered = []        #: List of the project modules ordered
 

	def __init__(self, controller, name = None, dir = None):
		OTModule.__init__(self, name)

		self._modules = {}
		self._modulesOrdered = []
	
		self._projectDir = dir
		self.controller = controller

	############################################################################
	############ Project functions  ############################################
	############################################################################

	def openProject(self, projectDir, file):
		"""
		Open a project
		@param projectDir: Project directory
		@type projectDir: String
		@param file: Project file name
		@type file: String
		"""

		#try:
		self._projectDir = projectDir
		filename = '%s/%s' % (self._projectDir, file)
		try:
			pkl_file = open(filename, 'rb'); project_data = pickle.load(pkl_file); pkl_file.close()
		except Exception, err:
			print str(err)
			if( os.path.isfile(filename+'.bak') ):
				QtGui.QMessageBox.critical(None, "Error", "Sorry there was an error importing the project!\nWe detect a backup from a previous version of the project, and we will import it instead!")
				#Open the backup file in case of error
				pkl_file = open(filename+".bak", 'rb'); project_data = pickle.load(pkl_file); pkl_file.close()
		
		data = dict(project_data)
		self.load(project_data)
		self.moduleUpdatedEvent(self)
		return data
		

	def saveProject(self, project_data = {} ):
		"""Save project"""
		filename = '%s/%s' % (self._projectDir, "project.ot")
		if( os.path.isfile(filename) ):
			try:
				os.remove(filename+".bak")
			except Exception, err:
				print str(err)
			os.rename(filename, filename+".bak" )
		self.project_data = project_data
		self.save(project_data)

		output = open(filename, 'wb')
		pickle.dump(self.project_data, output)
		output.close()

	def findModulesWithName(self, name):
		haveSameName = []
		for mod in self.modulesOrdered:
			if mod.name==name: haveSameName.append(mod)
		return haveSameName


	def __add__(self, module):
		"""
		Add module to the project
		@param module: Module object
		@type module: OTModule
		"""
		#check if the name exists:
		haveSameName = self.findModulesWithName(module.name)
		if len(haveSameName)>0: module.name += ' '+str(len(haveSameName))
		####################################
		module.parentModule = self
		self._modules[module.uid] = module
		self._modulesOrdered.append(module)
		

		self.addModuleEvent(module)
		self.moduleUpdatedEvent(self)

		for mod in self._modulesOrdered: mod.updateControls()
		return self

	def __sub__(self, module):
		"""
		Remove module from the project
		@param module: Module object
		@type module: OTModule
		"""
		del self._modules[module.uid]
		self._modulesOrdered.remove(module)
		self.moduleUpdatedEvent(self)

		for mod in self._modulesOrdered: mod.updateControls()

		return self

	


	############################################################################
	############ Parent class functions reemplementation #######################
	############################################################################

	def close(self):
		"""
		OTModule.close reimplementation
		"""
		for mod in self.modulesOrdered:
			print "Closing module %s" % mod.name
			mod.close()
		

	def save(self, saver):
		"""
		OTModule.saveContent reimplementation
		"""
		OTModule.save(self, saver)
		saver['childs'] = []
		for module in self.modulesOrdered:
			dataToSave = {}
			module.save(dataToSave)
			saver['childs'].append(dataToSave)

	def load(self, loader):
		"""
		OTModule.loadContent reimplementation
		"""
		OTModule.load(self, loader)
		for saved in loader['childs']:
			module = saved['class'](saved['name'])
			self += (module)
			if isinstance(module, BaseWidget): module.initForm()
			uid2Remove = self._modulesOrdered[-1].uid
			module.load(saved)
			del self._modules[uid2Remove]
			self._modules[module.uid] = module
			


	############################################################################
	############ Events ########################################################
	############################################################################

	def moduleUpdatedEvent(self, module):
		"""
		Event called when a project module is updated
		@param module: the project was updated
		@type module: OTModuleProject
		"""
		pass

	def addModuleEvent(self, module):
		"""
		Event called when a module is added to the project
		@param module: A new module was added to the project
		@type module: OTModuleProject
		"""
		pass

	############################################################################
	############ Properties ####################################################
	############################################################################

	@property
	def modulesOrdered(self):
		"""Return all the project modules ordered"""
		if self._modulesOrdered == None:
			return []
		else:
			return self._modulesOrdered

	############################################################################

	@property
	def controller(self):
		"""Return the controller"""
		return self._controller

	@controller.setter
	def controller(self, value): self._controller = value