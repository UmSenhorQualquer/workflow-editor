from core.modules.base.OTModulePlugin import OTModulePlugin
from core.modules.formcontrols.OTControlBase import OTControlBase
from core.modules.formcontrols.OTParamGeometry import OTParamGeometry
from core.modules.formcontrols.OTParamFile import OTParamFile
from core.modules.formcontrols.OTParamSlider import OTParamSlider
from core.modules.formcontrols.OTParamPlayer import OTParamPlayer

import core.utils.tools as tools
from core.modules.modulestypes.OTModuleInputVideo import OTModuleInputVideo
from core.modules.formcontrols.OTParamProgress import OTParamProgress
from core.plugins.Inputs.OTModuleVideoInput.OTPOpenVideo import OTPOpenVideo

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import cv2, os

class OTModuleVideoInput(OTModulePlugin, OTModuleInputVideo):

    def __init__(self, name):
        icon_path = tools.getFileInSameDirectory(__file__, 'iconvi.jpg')
        super(OTModuleVideoInput, self).__init__(name, iconFile = icon_path)
        OTModuleInputVideo.__init__(self)
    
        self._file = OTParamFile("File")
        self._player = OTParamPlayer("Video", varname='__capture')
        self._progress = OTParamProgress()

        self._formset = [ "_file", "_player", "_progress" ]
        
        self._file.valueUpdated = self.videoSelected
        self._progress.hide()


    def videoSelected(self, value):
        OTParamFile.valueUpdated(self._file,value)
        self.open(value)
        self._player.value = self




    def exportCodeTo(self, folder):
        constructer_params = []
        parameters = []
        file_to_copy = 'OTPOpenVideo'
        imports = ["from %s import %s" % (file_to_copy, file_to_copy)]
        filename = file_to_copy+".py"; originalfilepath = tools.getFileInSameDirectory(__file__, filename); destinyfilepath = os.path.join( folder, filename )
        f = open(originalfilepath, 'r'); text = f.read(); f.close(); text = text.replace("from core.controllers.", "from "); f = open(destinyfilepath, 'w'); f.write(text); f.close()
        return [file_to_copy], imports, constructer_params, parameters       