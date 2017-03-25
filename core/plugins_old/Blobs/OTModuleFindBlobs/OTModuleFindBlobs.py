from core.modules.base.OTModulePlugin import OTModulePlugin
from core.modules.formcontrols.OTParamVideoInput import OTParamVideoInput
from core.modules.formcontrols.OTParamButton import OTParamButton
from core.modules.formcontrols.OTParamBackground import OTParamBackground
from core.modules.formcontrols.OTParamSlider import OTParamSlider
from core.modules.formcontrols.OTParamPlayer import OTParamPlayer
from core.modules.formcontrols.OTParamCheckBox import OTParamCheckBox
from core.modules.formcontrols.OTParamProgress import OTParamProgress
from core.modules.formcontrols.OTParamCombo import OTParamCombo
from core.modules.formcontrols.OTParamText import OTParamText
from core.modules.formcontrols.OTParamGeometry import OTParamGeometry

import cv2
import core.utils.tools as tools

from OTPFindBlobs import OTPFindBlobs
from core.plugins.Blobs.OTModuleBlobs import OTModuleBlobs


class OTModuleFindBlobs(OTModulePlugin, OTPFindBlobs, OTModuleBlobs):

    def __init__(self, name):
        icon_path = tools.getFileInSameDirectory(__file__, 'iconsubbg.jpg')
        OTModulePlugin.__init__(self, name,  iconFile=icon_path)
        OTPFindBlobs.__init__(self)

        self._video = OTParamVideoInput("Video")
        self._player = OTParamPlayer("Video player")

        self._minArea = OTParamSlider("Blob min. area", 100,   0,  50000, varname='_param_min_area')
        self._maxArea = OTParamSlider("Blob max. area", 10000, 0, 100000, varname='_param_max_area')

        self._formset = [ '_video', ('_minArea','_maxArea'), "_player" ]
        
        self._player.processFrame = self.processFrame
        self._video.valueUpdated = self.newVideoInputChoosen


    def processFrame(self, frame):
        blobs = self.process(frame)
        for blob in blobs: blob.draw(frame)
        return frame

    def newVideoInputChoosen(self, value):
        OTParamVideoInput.valueUpdated(self._video,value)
        if value: self._player.value = value