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
from core.modules.modulestypes.OTModuleInputVideo import OTModuleInputVideo

from core.plugins.Geometry.OTModuleMaskFromGeometry.OTModuleMaskFromGeometry import OTModuleMaskFromGeometry

from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from PyQt4 import QtSql

from numpy import *
from math import *
import cv2, os, time, itertools, shutil

from OTPRemoveBackground import OTPRemoveBackground
from OTPColorFilter import OTPColorFilter
from OTPBlur import OTPBlur
from OTPFindBlobs import OTPFindBlobs
from OTPSelectBiggerBlobs import OTPSelectBiggerBlobs
from OTPMaskImage import OTPMaskImage
from OTPAdaptativeThreshold import OTPAdaptativeThreshold
from OTPCanny import OTPCanny

class OTModuleColorFilter(OTModulePlugin,OTModuleInputVideo,OTModulePositions, OTPRemoveBackground, OTPColorFilter, OTPAdaptativeThreshold, OTPBlur, OTPMaskImage,OTPCanny, OTPFindBlobs, OTPSelectBiggerBlobs):
    

    def __init__(self, name):
        icon_path = tools.getFileInSameDirectory(__file__, 'iconsubbg.jpg')
        OTPRemoveBackground.__init__(self)
        OTPColorFilter.__init__(self)        
        OTPAdaptativeThreshold.__init__(self)
        OTPBlur.__init__(self)
        OTPFindBlobs.__init__(self)
        OTPSelectBiggerBlobs.__init__(self)
        OTPMaskImage.__init__(self)
        OTPCanny.__init__(self)
        OTModulePlugin.__init__(self, name,  iconFile=icon_path)

        self._video = OTParamVideoInput("Video")
        #self._polygons = OTParamGeometry("Geometry")
        self._background = OTParamBackground("Background", varname='_param_background')
        self._threshold = OTParamSlider("Threshold", 110, 1, 255, varname='_param_background_threshold')
        self._minArea = OTParamSlider("Blob min. area",100, 0, 50000, varname='_param_min_area')
        self._maxArea = OTParamSlider("Blob max. area", 10000, 0, 100000, varname='_param_max_area')
        self._textAlgo = OTParamText("Blob function ( Operations: [ AND: * ; OR: + ; SUB: - ; NEG: ~ ] Ex: A+B-~C )", "A*B*C", varname='_param_filter_algorithm')
        self._removeBg = OTParamCheckBox("Remove the background", True)
        
        self._player = OTParamPlayer("Video player")

        self._selectBiggests = OTParamCheckBox("Select only the biggests blobs", True)
        self._howMany = OTParamSlider("How many?", 1, 1, 20, varname='_param_n_blobs')

        self._useBlur = OTParamCheckBox("Use blur", True)
        self._kernelSize = OTParamSlider("Kernel size",1, 1, 50, varname='_param_kernel_size')
        self._blurThreshold = OTParamSlider("Blur threshold", 110, 1, 255, varname='_param_blur_threshould')
        
        self._colorDomain = OTParamCombo("Colors space", varname='_param_color_domain')
        self._colorDomain.addItem("RGB", -1)
        self._colorDomain.addItem("XYZ",    cv2.COLOR_BGR2XYZ)
        self._colorDomain.addItem("YCrCb",  cv2.COLOR_BGR2YCR_CB)
        self._colorDomain.addItem("HSV",    cv2.COLOR_BGR2HSV)
        self._colorDomain.addItem("HLS",    cv2.COLOR_BGR2HLS)
        self._colorDomain.addItem("Lab",    cv2.COLOR_BGR2LAB)
        self._colorDomain.addItem("Luv",    cv2.COLOR_BGR2LUV)

        self._activeR = OTParamCheckBox("Active")
        self._activeG = OTParamCheckBox("Active")
        self._activeB = OTParamCheckBox("Active")

        self._minR = OTParamSlider("min. A", 1, 0, 255, varname='_param_a_min')
        self._maxR = OTParamSlider("max. A", 255, 0, 255, varname='_param_a_max')
        self._minG = OTParamSlider("min. B", 1, 0, 255, varname='_param_b_min')
        self._maxG = OTParamSlider("max. B", 255, 0, 255, varname='_param_b_max')
        self._minB = OTParamSlider("min. C", 1, 0, 255, varname='_param_c_min')
        self._maxB = OTParamSlider("max. C", 255, 0, 255, varname='_param_c_max')


        #THRESHOLD 
        self._blockSize = OTParamSlider("Block size", 3, 3, 500,varname='_param_tb_block_size')
        self._C = OTParamSlider("C", 0, 0, 500,varname='_param_tb_c')
        self._boxWidth = OTParamSlider("Width", 0, 0, 30,varname='_param_tb_box_width')
        self._boxHeight = OTParamSlider("Height", 0, 0, 30,varname='_param_tb_box_height')
        self._adaptiveMethod = OTParamCombo("Adaptive method",varname='_param_tb_adaptive_method')
        self._adaptiveMethod.addItem("Mean", cv2.cv.CV_ADAPTIVE_THRESH_MEAN_C)
        self._adaptiveMethod.addItem("Gaussian", cv2.cv.CV_ADAPTIVE_THRESH_GAUSSIAN_C)
        
        self._th_colorDomain = OTParamCombo("Colors space",varname='_param_tb_color_domain')
        self._th_colorDomain.addItem("RGB", -1)
        self._th_colorDomain.addItem("Gray",   cv2.COLOR_BGR2GRAY)
        self._th_colorDomain.addItem("XYZ",    cv2.COLOR_BGR2XYZ)
        self._th_colorDomain.addItem("YCrCb",  cv2.COLOR_BGR2YCR_CB)
        self._th_colorDomain.addItem("HSV",    cv2.COLOR_BGR2HSV)
        self._th_colorDomain.addItem("HLS",    cv2.COLOR_BGR2HLS)
        self._th_colorDomain.addItem("Lab",    cv2.COLOR_BGR2LAB)
        self._th_colorDomain.addItem("Luv",    cv2.COLOR_BGR2LUV)
        
        self._colorComponent = OTParamCombo("Component",varname='_param_tb_color_component')
        self._colorComponent.addItem("A", 0)
        self._colorComponent.addItem("B", 1)
        self._colorComponent.addItem("C", 2)

        self._th_thresholdType = OTParamCombo("ThresholdType",varname='_param_tb_threshold_type')
        self._th_thresholdType.addItem("THRESH_BINARY", cv2.THRESH_BINARY)
        self._th_thresholdType.addItem("THRESH_BINARY_INV", cv2.THRESH_BINARY_INV)
        #END THRESHOLD


        #CANNY
        self._canny_apertureSize = OTParamSlider("Aperture size", 3, 3, 7, varname='_param_canny_apertureSize')
        self._canny_L2gradient = OTParamCheckBox("L2 gradient", True, varname='_param_canny_L2gradient')
        self._canny_threshould1 = OTParamSlider("Threshould 1", 0, 0, 255, varname='_param_canny_threshould1')
        self._canny_threshould2 = OTParamSlider("Threshould 2", 1, 0, 255, varname='_param_canny_threshould2')

        self._canny_colorDomain = OTParamCombo("Colors space",varname='_param_canny_color_domain')
        self._canny_colorDomain.addItem("RGB", -1)
        self._canny_colorDomain.addItem("Gray",   cv2.COLOR_BGR2GRAY)
        self._canny_colorDomain.addItem("XYZ",    cv2.COLOR_BGR2XYZ)
        self._canny_colorDomain.addItem("YCrCb",  cv2.COLOR_BGR2YCR_CB)
        self._canny_colorDomain.addItem("HSV",    cv2.COLOR_BGR2HSV)
        self._canny_colorDomain.addItem("HLS",    cv2.COLOR_BGR2HLS)
        self._canny_colorDomain.addItem("Lab",    cv2.COLOR_BGR2LAB)
        self._canny_colorDomain.addItem("Luv",    cv2.COLOR_BGR2LUV)
        
        self._canny_colorComponent = OTParamCombo("Component",varname='_param_canny_color_component')
        self._canny_colorComponent.addItem("A", 0)
        self._canny_colorComponent.addItem("B", 1)
        self._canny_colorComponent.addItem("C", 2)
        #END CANNY


        self._useColors = OTParamCheckBox("Use colors filter", True)
        self._useThreshold = OTParamCheckBox("Use adaptative threshold", False)
        self._useCanny = OTParamCheckBox("Use canny algorithm", False)        
        self._exportFindBlobs = OTParamCheckBox("Export find blobs", True)

        self._canny_colorDomain.valueUpdated = self.refreshValue
        self._canny_colorComponent.valueUpdated = self.refreshValue
        self._canny_apertureSize.valueUpdated = self.refreshValue
        self._canny_L2gradient.valueUpdated = self.refreshValue
        self._canny_threshould1.valueUpdated = self.refreshValue
        self._canny_threshould2.valueUpdated = self.refreshValue
        self._th_colorDomain.valueUpdated = self.refreshValue
        self._colorComponent.valueUpdated = self.refreshValue
        self._adaptiveMethod.valueUpdated = self.refreshValue
        self._boxHeight.valueUpdated = self.refreshValue
        self._boxWidth.valueUpdated = self.refreshValue
        self._blockSize.valueUpdated = self.refreshValue
        self._C.valueUpdated = self.refreshValue

        
        self._colorDomain.valueUpdated = self.refreshValue
        self._activeR.valueUpdated = self.refreshValue
        self._activeG.valueUpdated = self.refreshValue
        self._activeB.valueUpdated = self.refreshValue
        self._minR.valueUpdated = self.refreshValue
        self._maxR.valueUpdated = self.refreshValue
        self._minG.valueUpdated = self.refreshValue
        self._maxG.valueUpdated = self.refreshValue
        self._minB.valueUpdated = self.refreshValue
        self._maxB.valueUpdated = self.refreshValue

        self._textAlgo.valueUpdated = self.refreshValue
        self._threshold.valueUpdated = self.refreshValue
        self._kernelSize.valueUpdated = self.refreshValue
        self._blurThreshold.valueUpdated = self.refreshValue
        self._maxArea.valueUpdated = self.refreshValue
        self._minArea.valueUpdated = self.refreshValue

        self._removeBg.valueUpdated = self.removeBgUpdate
        self._useBlur.valueUpdated = self.useBlurUpdate
        self._selectBiggests.valueUpdated = self.selectBiggestsUpdate
    
        self._useColors.valueUpdated = self.__useColorsClicked
        self._useThreshold.valueUpdated = self.__useThresholdClicked
        self._useCanny.valueUpdated = self.__useCannyClicked
        
        self._formset = [ 
                ('_video',' ','_useColors','_useThreshold','_useCanny'),
                [
                    "_player",{
                        "Remove background": [ '_removeBg','_background', '_threshold'],
                        "Filter colors" :  ['_colorDomain', ("_minR",'_activeR',"_maxR"), ("_minG",'_activeG',"_maxG"),  ("_minB",'_activeB',"_maxB")],
                        "Threshold filter": [('_th_colorDomain','_colorComponent','_adaptiveMethod','_th_thresholdType'), ('_boxWidth', '_boxHeight'),('_blockSize',"_C")],
                        "Canny": [ ('_canny_colorDomain', '_canny_colorComponent'), '_canny_threshould1','_canny_threshould2','_canny_apertureSize','_canny_L2gradient'],
                        "Filter objects": [ ('_minArea', '_maxArea'), ('_useBlur', '_kernelSize', '_blurThreshold'), ("_selectBiggests", "_howMany"),'_exportFindBlobs' ],
                    },"_textAlgo"                    
                ]
            ]
        
        self._player.processFrame = self.processFrame
        self._video.valueUpdated = self.newVideoInputChoosen

        self._blurThreshold.hide()
        self._kernelSize.hide()
        self._background.hide()
        self._threshold.hide()
        self._howMany.hide()

    def __useColorsClicked(self, value):
        
        if value==2:
            self._useCanny.enabled = True
            self._useThreshold.enabled = True
            self._useThreshold.uncheck()
            self._useCanny.uncheck()
            self._useColors.enabled = False
            self.hideTab("Threshold filter")
            self.showTab("Filter colors")
            self.hideTab("Canny")
            self._player.refresh()

    def __useThresholdClicked(self, value):
        if value==2:
            self._useCanny.enabled = True
            self._useColors.enabled = True
            self._useCanny.uncheck()
            self._useColors.uncheck()
            self._useThreshold.enabled = False
            self.showTab("Threshold filter")
            self.hideTab("Filter colors")
            self.hideTab("Canny")
            self._player.refresh()

    def __useCannyClicked(self, value):
        if value==2:
            self._useThreshold.enabled = True
            self._useColors.enabled = True
            self._useThreshold.uncheck()
            self._useColors.uncheck()
            self._useCanny.enabled = False
            self.hideTab("Threshold filter")
            self.hideTab("Filter colors")
            self.showTab("Canny")
            self._player.refresh()


    def initForm(self):
        super(OTModuleColorFilter, self).initForm()
        self.hideTab("Threshold filter")
        self.hideTab("Canny")

    def refreshValue(self, value):
        self._player.refresh()

    def selectBiggestsUpdate(self, value):
        if value:
            self._howMany.show()
        else:
            self._howMany.hide()
        self._player.refresh()

    def useBlurUpdate(self, value):
        if value:
            self._kernelSize.show()
            self._blurThreshold.show()
        else:
            self._kernelSize.hide()
            self._blurThreshold.hide()
        self._player.refresh()

        


    def removeBgUpdate(self, value):
        if value:
            self._background.show()
            self._threshold.show()
        else:
            self._background.hide()
            self._threshold.hide()
        self._player.refresh()

    def newVideoInputChoosen(self, value):
        OTParamVideoInput.valueUpdated(self._video,value)
        if value:
            self._player.value = value
            self.videoInput = value

            if isinstance(value, OTModuleMaskFromGeometry):
                self._param_mi_polygons = value._all_polygons
                self._param_mi_mask = None

    def processFrame(self, frame):
        original = frame.copy()
        
        if self._removeBg.value: 
            self._param_background = self._background.value
            frame = OTPRemoveBackground.compute(self, frame)

        if self._useThreshold.value:
            fish = OTPAdaptativeThreshold.compute(self, frame)
        elif self._useCanny.value:
            fish = OTPCanny.compute(self, frame)
        else:
            fish = OTPColorFilter.compute(self, frame)

        if self._useBlur.value: fish = OTPBlur.compute(self, fish)


        if isinstance(self._video.value, OTModuleMaskFromGeometry):
            fish = OTPMaskImage.compute(self, fish)

        self._objectsFound = OTPFindBlobs.compute(self, fish)

        """
        for obj in self._objectsFound:
            mask = zeros_like(original)
            cv2.fillPoly( mask, obj._contour, (255, 255, 255) )
            res = cv2.bitwise_and(original, mask)
            b,g,r = cv2.split(res)
            b_avg = mean(b[b>0])
            g_avg = mean(g[g>0])
            r_avg = mean(r[r>0])
            obj._color = b_avg, g_avg, r_avg
        """
        if self._selectBiggests.value: self._objectsFound = OTPSelectBiggerBlobs.compute(self, self._objectsFound)
            
        ################################################################
        ################################################################

        contours2Display = []
        for obj in self._objectsFound:  contours2Display.append( obj._contour )

        cv2.drawContours( frame, array(contours2Display), -1, (0, 255, 0), 1 )


        for i, obj in enumerate(self._objectsFound):
            cv2.circle(frame, obj._centroid, 5, (255,0,0), thickness=1)
            p = obj._bounding[0]
            text = "AREA: %d" % obj._area
            #cv2.putText(frame, text, p , cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255),  3)
            #cv2.putText(frame, text, p , cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255),         1)    

        if self._useColors.value:
            if self._removeBg.value: original = OTPRemoveBackground.compute(self, original)
            if self._colorDomain.value>=0: original = cv2.cvtColor(original, self._colorDomain.value)
            r,g,b = cv2.split( original )
            if not self._activeR.value: r = r * 0
            if not self._activeG.value: g = g * 0
            if not self._activeB.value: b = b * 0
            r = cv2.inRange(r, array(self._minR.value), array(self._maxR.value) )
            g = cv2.inRange(g, array(self._minG.value), array(self._maxG.value) )
            b = cv2.inRange(b, array(self._minB.value), array(self._maxB.value) )
            image = cv2.merge( (b,g,r) )
        
            return [frame, image, fish]
        else:
            return [frame, fish]











        

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