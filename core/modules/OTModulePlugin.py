
from core.modules.OTModuleWorkFlowItem import OTModuleWorkFlowItem
from core.modules.ModuleConnection import ModuleConnection
from PyQt4 import QtGui
#This class is a module that indicate that the input is of video type
from pyforms import BaseWidget

class OTModulePlugin(BaseWidget, OTModuleWorkFlowItem):
	"""
	Abstract class that implement a plugin
	"""
	def __init__(self, name, iconFile = None):
		if not iconFile: iconFile = tools.getFileInSameDirectory(__file__,"question.png")
		BaseWidget.__init__(self, name)
		OTModuleWorkFlowItem.__init__(self, name, iconFile=iconFile)

	def exportCodeTo(self, folder):
		QtGui.QMessageBox.information(
			self.form,
			"Code not exported", "Sorry export not implemented for this plugin: %s" % self._name )

	def getExecutionTree(self, count=0):
		res = []
		for name, var in vars(self).items():
			if isinstance(var, ModuleConnection):
				m = var.value
				res += [(count, var)]
				res += m.getExecutionTree(count+1)
		return res

	def executePreviousTree(self):
		res = sorted(self.getExecutionTree(), key=lambda x: -x[0])
	
	def updateControls(self):
		for key, control in self.controls.items():
			if hasattr(control, 'updateControl'): 
				control.updateControl()
				control.changed_event()

	def save(self, saver):
		"""
		OTModule.saveContent reimplementation
		"""
		BaseWidget.save(self, saver)
		OTModuleWorkFlowItem.save(self, saver)

	def load(self, loader):
		"""
		OTModule.loadSavedContent reimplementation
		"""
		OTModuleWorkFlowItem.load(self, loader)
		BaseWidget.load(self, loader)


	@property
	def name(self): return str(self.title)

	@name.setter
	def name(self, value): self.title = value