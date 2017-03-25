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
from core.modules.formcontrols.OTParamModuleConnection import OTParamModuleConnection

import cv2
import core.utils.tools as tools

from OTPSelectBiggerBlobs import OTPSelectBiggerBlobs
from core.plugins.Blobs.OTModuleBlobs import OTModuleBlobs


class OTModuleLargestBlobs(OTModulePlugin, OTPSelectBiggerBlobs, OTModuleBlobs):

    def __init__(self, name):
        icon_path = tools.getFileInSameDirectory(__file__, 'iconsubbg.jpg')
        OTModulePlugin.__init__(self, name,  iconFile=icon_path)
        OTPSelectBiggerBlobs.__init__(self)

        self._video = OTParamVideoInput("Video")
        self._blobs  = OTParamModuleConnection("Blobs", connecting=OTModuleBlobs)
        self._player = OTParamPlayer("Video player")

        self._howMany = OTParamSlider("How many?", 1, 1, 20, varname='_param_n_blobs')

        self._formset = ['_video','_blobs', '_howMany', "_player" ]
        
        self._player.processFrame = self.processFrame
        self._video.valueUpdated = self.newVideoInputChoosen


    def processFrame(self, frame):
        print self.executePreviousTree()
        print "------"
        parent = self._blobs.value
        if parent:
            blobs = parent.process(frame)
            blobs = self.process(blobs)
            for blob in blobs: blob.draw(frame)
        return frame

    def newVideoInputChoosen(self, value):
        OTParamVideoInput.valueUpdated(self._video,value)
        if value: self._player.value = value