from core.modules.base.OTModulePlugin import OTModulePlugin
from core.modules.formcontrols.OTParamGeometry import OTParamGeometry
from core.modules.formcontrols.OTParamPlayer import OTParamPlayer
from core.modules.formcontrols.OTParamVideoInput import OTParamVideoInput
from core.modules.formcontrols.OTParamModuleConnection import OTParamModuleConnection

from core.plugins.Geometry.base.OTBaseModuleGeometry import OTBaseModuleGeometry
from core.modules.modulestypes.OTModuleInputVideoPipe import OTModuleInputVideoPipe
from core.datatypes.video.OTVideoMask import OTVideoMask

import core.utils.tools as tools
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from numpy import *
import cv2, os

class OTModuleMaskFromGeometry(OTModulePlugin, OTModuleInputVideoPipe):

    def __init__(self, name):
        icon_path = tools.getFileInSameDirectory(__file__, 'iconmask.jpg')
        OTModulePlugin.__init__(self, name, iconFile = icon_path)
        OTModuleInputVideoPipe.__init__(self)

        self._polygons  = OTParamModuleConnection("Polygons", connecting=OTBaseModuleGeometry)
        self._video = OTParamVideoInput("Video")
        self._player = OTParamPlayer("Video")

        self._formset = [ '_video',"_polygons", "_player" ]

        self._video.valueUpdated = self.videoSelected
        self._polygons.valueUpdated = self.polygonsSelected
        self._player.processFrame = self.processFrame

        self._mask_color = None
        self._mask_gray = None


    def processFrame(self, frame):
        if len(frame.shape)>2:
            frame = cv2.bitwise_and(frame,self._mask_color) 
        else:
            frame = cv2.bitwise_and(frame,self._mask_gray) 
        return frame

    def videoSelected(self, value):
        OTParamVideoInput.valueUpdated(self._video,value)
        self.open(value)
        self._player.value = value

        self.polygonsSelected(self._polygons.value)
            

    def polygonsSelected(self, value):
        if value!=None:
            self._mask_color = zeros( (int(self._player.value.height), int(self._player.value.width), 3 ), dtype=uint8 )
            self._mask_gray = zeros( (int(self._player.value.height), int(self._player.value.width) ), dtype=uint8 )
            for poly in value.polygons: 
                cv2.fillPoly( self._mask_color, [array(poly,int32)], (255,255,255) )
                cv2.fillPoly( self._mask_gray, [array(poly,int32)], (255,255,255) )
            
        














    def exportCodeTo(self, folder):
        listOfPolygons = self._polygons.value._polygons.value
        polygons = [eval(poly) for name, poly in listOfPolygons]   
        parameters = ["self._params_mask_contours=np.array(%s)" % str(polygons)]
        constructer_params = []

        file_to_copy = 'OTPMaskFromGeometry'
        imports = ["from %s import %s" % (file_to_copy, file_to_copy),"import numpy as np"]
        filename = file_to_copy+".py"; originalfilepath = tools.getFileInSameDirectory(__file__, filename); destinyfilepath = os.path.join( folder, filename )
        f = open(originalfilepath, 'r'); text = f.read(); f.close(); text = text.replace("from core.controllers.", "from "); f = open(destinyfilepath, 'w'); f.write(text); f.close()
        return [file_to_copy], imports, constructer_params, parameters       