from core.modules.OTModule import OTModule
from PyQt4 import uic
import uuid
import os

class OTModuleProjectItem(OTModule):
	"""
	Abstract project module item abstract class implementation
	"""
	_parentModule = None    #: Parent module
	_iconFile = None        #: Module icon file name
	_form = None         #: PyQt interface object

	def __init__(self, name,  *args, **keys):
		super(OTModuleProjectItem, self).__init__(name)
		
		self._iconFile = keys['iconFile']
		self._parentModule = None
		if 'uiFile' in keys.keys(): self._form = uic.loadUi( keys['uiFile'] )

	def show(self): 
		"""
		Show the graphical interface of the module
		"""
		self.form.show()

	############################################################################
	############ Properties ####################################################
	############################################################################

	@property
	def parentModule(self): return self._parentModule

	@parentModule.setter
	def parentModule(self, value): self._parentModule = value

	############################################################################

	@property
	def form(self): return self._form

	############################################################################