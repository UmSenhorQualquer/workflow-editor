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
from core.modules.modulestypes.OTModuleInputVideoPipe import OTModuleInputVideoPipe

from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from PyQt4 import QtSql

from numpy import *
from math import *
import cv2, os, time, itertools, shutil

from OTPSplitColors import OTPSplitColors

class OTModuleSplitColors(OTModulePlugin,OTModuleInputVideoPipe,OTPSplitColors):
    

    def __init__(self, name):
        icon_path = tools.getFileInSameDirectory(__file__, 'iconsubbg.jpg')
        OTPSplitColors.__init__(self)        
        OTModulePlugin.__init__(self, name,  iconFile=icon_path)

        self._video = OTParamVideoInput("Video")
        self._player = OTParamPlayer("Video player")

        self._colorComponent = OTParamCombo("Component",varname='_split_color_channel')
        self._colorComponent.addItem("A", 0)
        self._colorComponent.addItem("B", 1)
        self._colorComponent.addItem("C", 2)

        self._colorComponent.valueUpdated = self.refreshValue

        self._formset = [ 
                '_video',
                '_colorComponent',
                "_player",
            ]
        
        self._player.processFrame = self.processFrame
        self._video.valueUpdated = self.newVideoInputChoosen

    def refreshValue(self, value): self._player.refresh()


    def newVideoInputChoosen(self, value):
        OTParamVideoInput.valueUpdated(self._video,value)
        if value:
            self.open(value)
            self._player.value = value
            

    def processFrame(self, frame):
        filtered = OTPSplitColors.compute(self, frame)
        return [frame, filtered]



        

    def exportCodeTo(self, folder):
        files_to_copy = []        
        classes, imports, constructer_params, parameters = [], [], [], []
        #classes_tmp, imports_tmp, constructer_params_tmp, parameters_tmp = self._video.value.exportCodeTo(folder)
        #classes += classes_tmp; imports += imports_tmp; constructer_params += constructer_params_tmp; parameters += parameters_tmp;

        #SET OTPRemoveBackground
        if self._removeBg.value:
            classes_tmp, imports_tmp, constructer_params_tmp, parameters_tmp = self._background.value.exportCodeTo(folder)
            classes += classes_tmp; imports += imports_tmp; constructer_params += constructer_params_tmp; parameters += parameters_tmp;
            files_to_copy.append( 'OTPRemoveBackground' )
            parameters.append("self._param_background_threshold = %d " % self._threshold.value )
        #END SET

        

        if self._useThreshold.value:
            #SET OTPAdaptativeThreshold
            files_to_copy.append( 'OTPAdaptativeThreshold' )
            parameters.append("self._param_tb_color_component = %d " % self._colorComponent.value )
            parameters.append("self._param_tb_color_domain = %d " % self._th_colorDomain.value )
            parameters.append("self._param_tb_adaptive_method = %d " % self._adaptiveMethod.value )
            parameters.append("self._param_tb_block_size = %d " % self._blockSize.value )
            parameters.append("self._param_tb_threshold_type = %d " % self._th_thresholdType.value )
            parameters.append("self._param_tb_c = %d " % self._C.value )
            #END SET
        elif self._useCanny.value:
            #SET OTPCanny
            files_to_copy.append( 'OTPCanny' )
            parameters.append("self._param_canny_apertureSize = %d " % self._canny_apertureSize.value )
            parameters.append("self._param_canny_L2gradient = %d " % self._canny_L2gradient.value )
            parameters.append("self._param_canny_threshould1 = %d " % self._canny_threshould1.value )
            parameters.append("self._param_canny_threshould2 = %d " % self._canny_threshould2.value )
            parameters.append("self._param_canny_color_component = %d " % self._canny_colorComponent.value )
            parameters.append("self._param_canny_color_domain = %d " % self._canny_colorDomain.value )
            #END SET
        else:
            #SET OTPColorFilter
            files_to_copy.append( 'OTPColorFilter' )
            parameters.append("self._param_color_domain = %d " % self._colorDomain.value )
            parameters.append("self._param_filter_algorithm = '%s' " % self._textAlgo.value )
            parameters.append("self._param_a_min = %d " % self._minR.value )
            parameters.append("self._param_a_max = %d " % self._maxR.value )
            parameters.append("self._param_b_min = %d " % self._minG.value )
            parameters.append("self._param_b_max = %d " % self._maxG.value )
            parameters.append("self._param_c_min = %d " % self._minB.value )
            parameters.append("self._param_c_max = %d " % self._maxB.value )
            #END SET

        #SET OTPBlur
        if self._useBlur.value: 
            files_to_copy.append( 'OTPBlur' )
            parameters.append("self._param_kernel_size = %d " % self._kernelSize.value )
            parameters.append("self._param_blur_threshould = %d " % self._blurThreshold.value )
        #END SET

        #SET OTPMaskImage
        if isinstance(self._video.value, OTModuleMaskFromGeometry):
            files_to_copy.append( 'OTPMaskImage' )
            parameters.append("self._param_mi_polygons = np.array(%s)" % str(self._video.value._all_polygons) )
            imports.append("import numpy as np")        
        #END SET
        
        #SET OTPFindBlobs
        if self._exportFindBlobs.value:
            files_to_copy.append( 'OTPFindBlobs' )
            parameters.append("self._param_min_area = %d " % self._minArea.value )
            parameters.append("self._param_max_area = %d " % self._maxArea.value )
        #END SET

        #SET OTPSelectBiggerBlobs
        if self._selectBiggests.value: 
            files_to_copy.append( 'OTPSelectBiggerBlobs' )
            parameters.append('self._param_n_blobs = %d' % self._howMany.value )
        #END SET

        classes += files_to_copy
        for file_to_copy in files_to_copy:
            filename = file_to_copy+".py"; originalfilepath = tools.getFileInSameDirectory(__file__, filename); destinyfilepath = os.path.join( folder, filename )            
            f = open(originalfilepath, 'r'); text = f.read(); f.close(); text = text.replace("from core.controllers.", "from "); f = open(destinyfilepath, 'w'); f.write(text); f.close()
            imports.append( "from %s import %s" % (file_to_copy, file_to_copy) )
        
        return classes, imports, constructer_params, parameters