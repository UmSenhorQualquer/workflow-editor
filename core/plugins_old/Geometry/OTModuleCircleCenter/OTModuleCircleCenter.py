from core.modules.base.OTModulePlugin import OTModulePlugin
from core.modules.formcontrols.OTControlBase import OTControlBase
from core.modules.formcontrols.OTParamButton import OTParamButton
from core.modules.formcontrols.OTParamSlider import OTParamSlider
from core.modules.formcontrols.OTParamPlayer import OTParamPlayer
from core.modules.formcontrols.OTParamToggle import OTParamToggle
from core.modules.formcontrols.OTParamList import OTParamList
from core.modules.formcontrols.OTParamVideoInput import OTParamVideoInput

from core.utils.tools import createRectanglePoints, createEllipsePoints
import core.utils.tools as tools
from FindCircle import FindCircle 

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import cv2
import numpy
import pickle

class OTModuleCircleCenter(OTModulePlugin):

    def __init__(self, name):
        icon_path = tools.getFileInSameDirectory(__file__, 'centre.png')
        super(OTModuleCircleCenter, self).__init__( name, iconFile = icon_path)

        
        self._video  = OTParamVideoInput("Video")
        self._player = OTParamPlayer("Video")
        self._run = OTParamButton("Run")

        self._formset = [ ('_video','_run'), "_player" ]

        self._video.valueUpdated = self.videoSelected
        self._run.value = self.__run
        
        self._center = None
        self._player.processFrame = self.processFrame
        
    @property
    def center(self): return self._center 
 

    def processFrame(self, frame):
        if self._center!=None: cv2.circle(frame, self._center, 10, (0,255,255), -1)    
        return frame


    def videoSelected(self, value):
        self._player.value = value
        
    def __run(self):
        finder = FindCircle()

        self._center = finder.find_circle_center( self._player.currentFrame )
        