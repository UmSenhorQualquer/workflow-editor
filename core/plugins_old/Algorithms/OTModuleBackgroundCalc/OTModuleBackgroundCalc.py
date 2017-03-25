from core.modules.base.OTModulePlugin import OTModulePlugin
from core.modules.formcontrols.OTParamVideoInput import OTParamVideoInput
from core.modules.formcontrols.OTParamButton import OTParamButton
from core.modules.formcontrols.OTParamSlider import OTParamSlider
from core.modules.formcontrols.OTParamButton import OTParamButton
from core.modules.formcontrols.OTParamPlayer import OTParamPlayer
from core.modules.formcontrols.OTParamCheckBox import OTParamCheckBox
from core.modules.formcontrols.OTParamProgress import OTParamProgress

import core.utils.tools as tools

#from core.plugins.OTModuleBackgroundCalc.OTPBackGroundDetector import OTPBackGroundDetector
from OTPBackGroundDetector import OTPBackGroundDetector
from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from PyQt4 import QtSql
from numpy import *
import cv2, os, shutil
import time

class OTModuleBackgroundCalc(OTModulePlugin):

    MHI_DURATION = 0.5
    MAX_TIME_DELTA = 0.25
    MIN_TIME_DELTA = 0.05


    def __init__(self, name):
        icon_path = tools.getFileInSameDirectory(__file__, 'iconbgcalc.jpg')
        OTModulePlugin.__init__(self, name, iconFile = icon_path)

        self._video = OTParamVideoInput("Video")
        
        self._jumpFrame = OTParamSlider("Frame jump step", 1000, 1, 4000)
        self._jump2Frame = OTParamSlider("Compare frame", 1500, 1, 4000)
        self._threshold = OTParamSlider("Threshold", 5, 0, 255)

        self._export = OTParamButton("Export")

        self._editMode = OTParamCheckBox("Edit mode", False)
        self._run = OTParamButton("Run")
        self._player = OTParamPlayer("Video player")
        self._progress = OTParamProgress()

        self._formset = [ ('_video', '_run', '_editMode','_export'), ( '_jumpFrame', '_jump2Frame', '_threshold'), "_player", "_progress" ]
        
        self._run.value = self.run
        self._player.processFrame = self.processFrame
        self._video.valueUpdated = self.newVideoInputChoosen

        self._export.value = self.export_clicked
        
        self._backgroundDetector = None
        self._progress.hide()

    def export_clicked(self):
        filename = str(QFileDialog.getSaveFileName(self._form, 'Choose a file', '') )
        if filename!="":
            cv2.imwrite(filename, self._backgroundDetector._background_color)
   
    def updateProgressBar(self, value ):
        self._progress.value = value
        QApplication.processEvents() 
            
    def run(self):
        video = self._video.value
        self._progress.show()
        self._progress.min = 0
        self._progress.value = 0 
        self._progress.max = video.videoInput.videoTotalFrames

        self._backgroundDetector = OTPBackGroundDetector(capture=video.videoInput, gaussianBlurMatrixSize=5, gaussianBlursigmaX=5, updateFunction=self.updateProgressBar)
        self._backgroundDetector.detect( self._jumpFrame.value, self._jump2Frame.value, self._threshold.value )

        self._progress.hide()
        

    def newVideoInputChoosen(self, value):
        OTParamVideoInput.valueUpdated(self._video,value)
        print type(value)
        if value.videoInput:
            self._player.value = value.videoInput
            value.videoInput.setFrame(0)

    def processFrame(self, frame):                
        if self._editMode.value and self._backgroundDetector!=None and self._backgroundDetector._background_color!=None and self._backgroundDetector.background!=None:
            return [self._backgroundDetector.background, frame, self._backgroundDetector._background_color]
        else:
            return frame


    def saveContent(self, saver):
        """
        OTModuleBackgroundCalc.saveContent reimplementation
        """
        OTModulePlugin.saveContent(self, saver)        
        if self._backgroundDetector!=None and self._backgroundDetector._background!=None:
            saver['_backgroundDetector'] = {}
            self._backgroundDetector.save( saver['_backgroundDetector'] )



    def loadSavedContent(self, loader):
        """
        OTModuleBackgroundCalc.loadSavedContent reimplementation
        """
        OTModulePlugin.loadSavedContent(self, loader) 
        
        if '_backgroundDetector' in loader:
            self._backgroundDetector = OTPBackGroundDetector(capture=self._video.value.videoInput)
            self._backgroundDetector.load( loader['_backgroundDetector'] )
        #elif self._video.value:
        #    self._backgroundDetector = BackGroundDetector(self._video.value.videoInput)
              
        

    def exportCodeTo(self, folder):        
        parameters = ['self._param_background_threshold=%d' % self._threshold.value]
        constructer_params = ['capture=capture']

        file_to_copy = 'OTPBackGroundDetector'
        imports = ["from %s import %s \n" % (file_to_copy, file_to_copy)]
        filename = file_to_copy+".py"; originalfilepath = tools.getFileInSameDirectory(__file__, filename); destinyfilepath = os.path.join( folder, filename )
        f = open(originalfilepath, 'r'); text = f.read(); f.close(); text = text.replace("from core.controllers.", "from "); f = open(destinyfilepath, 'w'); f.write(text); f.close()
        return [file_to_copy], imports, constructer_params, parameters