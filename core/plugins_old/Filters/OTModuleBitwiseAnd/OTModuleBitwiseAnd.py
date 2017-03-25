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

from core.modules.modulestypes.OTModuleInputVideoPipe import OTModuleInputVideoPipe
import core.utils.tools as tools

import cv2


class OTModuleBitwiseAnd(OTModulePlugin,OTModuleInputVideoPipe):
    

    def __init__(self, name):
        icon_path = tools.getFileInSameDirectory(__file__, 'iconsubbg.jpg')
        OTModulePlugin.__init__(self, name,  iconFile=icon_path)

        self._video1 = OTParamVideoInput("Video 1")
        self._video2 = OTParamVideoInput("Video 2")
        self._player = OTParamPlayer("Video player")
        
        self._formset = [ ('_video1','_video2'),"_player" ]
        
        self._player.processFrame = self.processFrame
        self._video1.valueUpdated = self.newVideoInputChoosen

    def processFrame(self, frame):
        self._video2.value.currentFrameIndex = self._video1.value.currentFrameIndex
        res, mask = self._video2.value.read()
        if len(frame.shape)<len(mask.shape):
            frame = cv2.merge( (frame,frame,frame) )
        if len(frame.shape)>len(mask.shape):
            mask = cv2.merge( (mask,mask,mask) )
        return cv2.bitwise_and(mask, frame)

    def newVideoInputChoosen(self, value):
        OTParamVideoInput.valueUpdated(self._video1,value)
        if value:
            self._player.value = value
            self.open(value)