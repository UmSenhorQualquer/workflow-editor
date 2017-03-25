from core.modules.OTModulePlugin import OTModulePlugin

import core.utils.tools as tools
from datatypes.TypeColorVideo import TypeColorVideo

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import cv2, os

from pyforms.Controls import ControlFile
from pyforms.Controls import ControlPlayer
from pyforms.Controls import ControlProgress

class OTModuleVideoInput(OTModulePlugin, TypeColorVideo):

	def __init__(self, name):
		OTModulePlugin.__init__(self, name, iconFile = tools.getFileInSameDirectory(__file__, 'iconvi.jpg'))
		TypeColorVideo.__init__(self)
	
		self._file      = ControlFile("File")
		self._player    = ControlPlayer("Video")

		self._formset = [ "_file", "_player"]
		
		self._file.changed_event = self.__videoSelected


	def __videoSelected(self):
		self.open( self._file.value )
		self._player.value = self


