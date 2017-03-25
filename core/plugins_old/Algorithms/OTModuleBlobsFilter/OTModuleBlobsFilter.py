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

import core.utils.tools as tools
from core.modules.modulestypes.OTModulePositions import OTModulePositions


from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from PyQt4 import QtSql

from numpy import *
from math import *
import cv2, os, time, itertools, shutil

from OTPThreshBlobs import OTPThreshBlobs
from OTPThreshImage import OTPThreshImage

from core.plugins.OTModuleColorFilter.OTModuleColorFilter import OTModuleColorFilter


class OTModuleBlobsFilter(OTModulePlugin,OTModulePositions, OTPThreshBlobs, OTPThreshImage):
    

    def __init__(self, name):
        icon_path = tools.getFileInSameDirectory(__file__, 'iconsubbg.jpg')
        OTModulePlugin.__init__(self, name,  iconFile=icon_path)
        OTPThreshImage.__init__(self)
        OTPThreshBlobs.__init__(self)
        self._video = OTParamVideoInput("Video")
        self._player = OTParamPlayer("Video player")
        self._polygons = OTParamGeometry("Geometry")
        
        self._blockSize = OTParamSlider("Block size", 3, 3, 500,varname='_param_tb_block_size')
        self._C = OTParamSlider("C", 0, 0, 500,varname='_param_tb_c')
        self._boxWidth = OTParamSlider("Width", 0, 0, 30,varname='_param_tb_box_width')
        self._boxHeight = OTParamSlider("Height", 0, 0, 30,varname='_param_tb_box_height')
        self._adaptiveMethod = OTParamCombo("Adaptive method",varname='_param_tb_adaptive_method')
        self._adaptiveMethod.addItem("Mean", cv2.cv.CV_ADAPTIVE_THRESH_MEAN_C)
        self._adaptiveMethod.addItem("Gaussian", cv2.cv.CV_ADAPTIVE_THRESH_GAUSSIAN_C)
        
        self._colorDomain = OTParamCombo("Colors space",varname='_param_tb_color_domain')
        self._colorDomain.addItem("RGB", -1)
        self._colorDomain.addItem("Gray",   cv2.COLOR_BGR2GRAY)
        self._colorDomain.addItem("XYZ",    cv2.COLOR_BGR2XYZ)
        self._colorDomain.addItem("YCrCb",  cv2.COLOR_BGR2YCR_CB)
        self._colorDomain.addItem("HSV",    cv2.COLOR_BGR2HSV)
        self._colorDomain.addItem("HLS",    cv2.COLOR_BGR2HLS)
        self._colorDomain.addItem("Lab",    cv2.COLOR_BGR2LAB)
        self._colorDomain.addItem("Luv",    cv2.COLOR_BGR2LUV)
        
        self._colorComponent = OTParamCombo("Component",varname='_param_tb_color_component')
        self._colorComponent.addItem("A", 0)
        self._colorComponent.addItem("B", 1)
        self._colorComponent.addItem("C", 2)

        self._formset = [ 
                ('_video','_polygons'),"_player",('_colorDomain','_colorComponent','_adaptiveMethod'), ('_boxWidth', '_boxHeight'),('_blockSize',"_C")
            ]

        self._colorDomain.valueUpdated = self.refreshValue
        self._colorComponent.valueUpdated = self.refreshValue
        self._adaptiveMethod.valueUpdated = self.refreshValue
        self._boxHeight.valueUpdated = self.refreshValue
        self._boxWidth.valueUpdated = self.refreshValue
        self._blockSize.valueUpdated = self.refreshValue
        self._C.valueUpdated = self.refreshValue
        
        self._player.processFrame = self.processFrame
        self._video.valueUpdated = self.newVideoInputChoosen

    def refreshValue(self, value):
        self._player.refresh()

    def newVideoInputChoosen(self, value):
        OTParamVideoInput.valueUpdated(self._video,value)
        if value.videoInput:
            self._player.value = value.videoInput
            value.videoInput.setFrame(0)

    def processFrame(self, frame):
        self._video.value.processFrame(frame.copy())
       
        if isinstance(self._video.value, OTModuleColorFilter):
            self._original_frame = frame
            blobs = OTPThreshBlobs.compute(self, self._video.value._objectsFound)
            for blob in blobs:
                p1, p2 = blob._tb_cut_bounding
                frame[p1[1]:p2[1],p1[0]:p2[0],2] = blob._tb_biggest_img
                blob.draw(frame)
        else:
            frame = OTPThreshImage.compute(self, frame)
            
        return [frame]



    def exportCodeTo(self, folder):
        files_to_copy = []        
        classes, imports, constructer_params, parameters = [], [], [], []
        classes_tmp, imports_tmp, constructer_params_tmp, parameters_tmp = self._video.value.exportCodeTo(folder)
        classes += classes_tmp; imports += imports_tmp; constructer_params += constructer_params_tmp; parameters += parameters_tmp;

        #SET OTPRemoveBackground
        if isinstance(self._video.value, OTModuleColorFilter):
            files_to_copy.append( 'OTPThreshBlobs' )
            parameters.append("self._param_tb_color_component = %d " % self._colorComponent.value )
            parameters.append("self._param_tb_color_domain = %d " % self._colorDomain.value )
            parameters.append("self._param_tb_adaptive_method = %d " % self._adaptiveMethod.value )
            parameters.append("self._param_tb_box_height = %d " % self._boxHeight.value )
            parameters.append("self._param_tb_box_width = %d " % self._boxWidth.value )
            parameters.append("self._param_tb_block_size = %d " % self._blockSize.value )
            parameters.append("self._param_tb_c = %d " % self._C.value )
        else:
            files_to_copy.append( 'OTPThreshImage' )
            parameters.append("self._param_tb_color_component = %d " % self._colorComponent.value )
            parameters.append("self._param_tb_color_domain = %d " % self._colorDomain.value )
            parameters.append("self._param_tb_adaptive_method = %d " % self._adaptiveMethod.value )
            parameters.append("self._param_tb_block_size = %d " % self._blockSize.value )
            parameters.append("self._param_tb_c = %d " % self._C.value )
        #END SET

    
        classes += files_to_copy
        for file_to_copy in files_to_copy:
            filename = file_to_copy+".py"; originalfilepath = tools.getFileInSameDirectory(__file__, filename); destinyfilepath = os.path.join( folder, filename )            
            f = open(originalfilepath, 'r'); text = f.read(); f.close(); text = text.replace("from core.controllers.", "from "); f = open(destinyfilepath, 'w'); f.write(text); f.close()
            imports.append( "from %s import %s" % (file_to_copy, file_to_copy) )
        
        return classes, imports, constructer_params, parameters