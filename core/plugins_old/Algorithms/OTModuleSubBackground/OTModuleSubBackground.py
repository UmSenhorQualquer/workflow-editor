from core.modules.formcontrols.OTParamVideoInput import OTParamVideoInput
from core.modules.formcontrols.OTParamButton import OTParamButton
from core.modules.formcontrols.OTParamBackground import OTParamBackground
from core.modules.formcontrols.OTParamSlider import OTParamSlider
from core.modules.formcontrols.OTParamPlayer import OTParamPlayer
from core.modules.formcontrols.OTParamCheckBox import OTParamCheckBox
from core.modules.formcontrols.OTParamProgress import OTParamProgress
from core.modules.formcontrols.OTParamCombo import OTParamCombo
from core.modules.formcontrols.OTParamText import OTParamText

import core.utils.tools as tools
from core.plugins.OTModuleResultsPlugin.OTModuleResultsPlugin import OTModuleResultsPlugin
from core.modules.modulestypes.OTModulePositions import OTModulePositions

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

class OTModuleSubBackground(OTModuleResultsPlugin, OTModulePositions, OTPRemoveBackground, OTPColorFilter, OTPBlur, OTPFindBlobs, OTPSelectBiggerBlobs):

    MHI_DURATION = 0.5
    MAX_TIME_DELTA = 0.25
    MIN_TIME_DELTA = 0.05

    _isRunning = None

    

    def __init__(self, name):
        icon_path = tools.getFileInSameDirectory(__file__, 'iconsubbg.jpg')
        OTPRemoveBackground.__init__(self)
        OTPColorFilter.__init__(self)
        OTPBlur.__init__(self)
        OTPFindBlobs.__init__(self)
        OTPSelectBiggerBlobs.__init__(self)
        OTModuleResultsPlugin.__init__(self, name, iconFile = icon_path)

        self._video = OTParamVideoInput("Video")
        self._background = OTParamBackground("Background", varname='_param_background')
        self._threshold = OTParamSlider("Threshold", 110, 1, 255, varname='_param_background_threshold')
        self._minArea = OTParamSlider("Blob min. area",100, 0, 50000, varname='_param_min_area')
        self._maxArea = OTParamSlider("Blob max. area", 10000, 0, 100000, varname='_param_max_area')
        self._textAlgo = OTParamText("Blob function ( Operations: [ AND: * ; OR: + ; SUB: - ; NEG: ~ ] Ex: A+B-~C )", "A*B*C", varname='_param_filter_algorithm')
        self._removeBg = OTParamCheckBox("Remove the background", True)
        self._editMode = OTParamCheckBox("Edit mode", True)
        self._run = OTParamButton("Run")
        self._player = OTParamPlayer("Video player")
        self._progress = OTParamProgress()

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

        self._groupBlobs = OTParamCheckBox("Group blobs", True)
        self._maxDistance = OTParamSlider("Max. dist. between blobs", 1, 30, 300)

        self._groupBlobs.valueUpdated = self.groupBlobsUpdated
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
        self._maxDistance.valueUpdated = self.refreshValue

        self._removeBg.valueUpdated = self.removeBgUpdate
        self._useBlur.valueUpdated = self.useBlurUpdate
        self._selectBiggests.valueUpdated = self.selectBiggestsUpdate

        self._formset = [ 
                ( '_video', '_editMode', '_run'),
                [
                    "_player", { 
                        "1. Filter colors" :  ['_colorDomain', ("_minR",'_activeR',"_maxR"), ("_minG",'_activeG',"_maxG"),  ("_minB",'_activeB',"_maxB"), "_textAlgo"],
                        "2. Remove background": [ '_removeBg','_background', '_threshold'],
                        "3. Filter objects": [ ('_minArea', '_maxArea'), ('_useBlur', '_kernelSize', '_blurThreshold'), ("_selectBiggests", "_howMany") ],
                        "4. Tracking": [ ('_groupBlobs', '_maxDistance') ],
                    },
                    "=","_results", "_query"
                ], 
                "_progress" 
            ]
        
        self._run.value = self.run
        self._player.processFrame = self.processFrame
        self._video.valueUpdated = self.newVideoInputChoosen

        
        self._isRunning = False

        self._blurThreshold.hide()
        self._kernelSize.hide()
        self._background.hide()
        self._threshold.hide()
        self._progress.hide()
        self._howMany.hide()
        self._results.hide()
        self._query.hide()
        self._maxDistance.hide()

    def refreshValue(self, value):
        self._player.refresh()

    def groupBlobsUpdated(self, value):
        if value:
            self._maxDistance.show()
        else:
            self._maxDistance.hide()
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

    def run(self):
        if self._isRunning==True: 
            self._isRunning = False
        else:

            self._run.label = "Cancel"
            self._isRunning = True
            
            video = self._video.value

            self._player.enabled = False
            self._query.enabled = False
            self._results.enabled = False
            self._minArea.enabled = False
            self._maxArea.enabled = False
            self._video.enabled = False
            self._background.enabled = False
            self._editMode.enabled = False
            self._colorDomain.enabled = False
            self._activeR.enabled = False
            self._activeG.enabled = False
            self._activeB.enabled = False
            self._minR.enabled = False
            self._maxR.enabled = False
            self._minG.enabled = False
            self._maxG.enabled = False
            self._minB.enabled = False
            self._maxB.enabled = False

            self._progress.show()
            self._progress.min = video.videoInput.startFrame
            self._progress.value = video.videoInput.startFrame
            self._progress.max = video.videoInput.endFrame

            QApplication.processEvents()

            query = QtSql.QSqlQuery( self.parentModule.sqldb )

            query.exec_("PRAGMA cache_size = 65536")
            query.exec_("PRAGMA temp_store = MEMORY")
            query.exec_("PRAGMA journal_mode = OFF")
            #query.exec_("PRAGMA locking_mode = EXCLUSIVE")
            query.exec_("PRAGMA synchronous = OFF")
            
            tablename = "%s_output" % (self.name.replace(" ", "").lstrip('0123456789.') )
            res = query.exec_("DROP TABLE IF EXISTS %s" % tablename)
            if not res: 
                print "trying to drop: ", query.lastError().text() 
                query.finish()
                query = QtSql.QSqlQuery( self.parentModule.sqldb )
                query.exec_("PRAGMA cache_size = 65536")
                query.exec_("PRAGMA temp_store = MEMORY")
                query.exec_("PRAGMA journal_mode = OFF")
                query.exec_("PRAGMA synchronous = OFF")
                res = query.exec_("DELETE FROM %s" % tablename)
                if not res: print "trying to delete: ", query.lastError().text() 
                self.parentModule.sqldb.commit()
            else: 
                query.exec_("CREATE TABLE if not exists %s(id INTEGER PRIMARY KEY AUTOINCREMENT, frame BIGINT, seconds DOUBLE, milliseconds BIGINT, x INTEGER, y INTEGER, polygon text, b INTEGER, g INTEGER, r INTEGER)" % tablename)

            success = True
            video.videoInput.setFrame(0)

            while( success and self._isRunning ):
                (success, frame) = video.videoInput.read()
                if success:
                    self.processFrame(frame)
                    milliseconds = video.videoInput.getCurrentFrame()*video.videoInput.videoFrameTimeInterval

                    for i, obj in enumerate(self._objectsFound):
                        centroid = obj._centroid
                        poly = obj._contour.tolist() #cv2.convexHull(obj['countour']).tolist()
                        b_avg = obj._b_avg
                        g_avg = obj._g_avg
                        r_avg = obj._r_avg
                        query.exec_( "INSERT INTO %s(  frame, seconds, milliseconds, x, y, polygon, b,g,r ) VALUES (%d,%f,%f,%d,%d,'%s', %d, %d, %d)" % (tablename, video.videoInput.getCurrentFrame(), milliseconds/1000.0, milliseconds,centroid[0], centroid[1], poly, b_avg, g_avg, r_avg ) )
                        
                    self._progress.value = video.videoInput.getCurrentFrame()
                    QApplication.processEvents()

            self._progress.value = video.videoInput.endFrame
            QApplication.processEvents()
            query.finish()
            self.parentModule.sqldb.commit()
            self._progress.hide()
            
            self._player.enabled = True
            self._query.enabled = True
            self._results.enabled = True
            self._minArea.enabled = True
            self._maxArea.enabled = True
            self._video.enabled = True
            self._background.enabled = True
            self._editMode.enabled = True

            self._colorDomain.enabled = True
            self._activeR.enabled = True
            self._activeG.enabled = True
            self._activeB.enabled = True
            self._minR.enabled = True
            self._maxR.enabled = True
            self._minG.enabled = True
            self._maxG.enabled = True
            self._minB.enabled = True
            self._maxB.enabled = True

            self._isRunning = False

            self._run.label = "Run"
            
            self._results.clearItems()
            self._results.addItem("Results", "SELECT id, frame, seconds, milliseconds, x, y, polygon, b,g,r FROM %s" % tablename)
            self._results.show()
            self._query.show()

    def newVideoInputChoosen(self, value):
        OTParamVideoInput.valueUpdated(self._video,value)
        if value.videoInput:
            self._player.value = value.videoInput
            value.videoInput.setFrame(0)










    def __calcObjectsDist( self, obj, objects_list ):
        results = []
        for x in objects_list:
            dist = tools.pointsDistance(obj._centroid, x._centroid)
            results.append( (dist, x) )
        return sorted(results, key=lambda x: x[0], reverse=True)


    def processFrame(self, frame):
        original = frame.copy()


        
        if self._removeBg.value: frame = OTPRemoveBackground.process(self, frame)
        fish = OTPColorFilter.process(self, frame)
        if self._useBlur.value: fish = OTPBlur.process(self, fish)
        
        self._objectsFound = OTPFindBlobs.process(self, fish)

        for obj in self._objectsFound:
            mask = zeros_like(original)
            cv2.fillPoly( mask, obj._contour, (255, 255, 255) )
            res = cv2.bitwise_and(original, mask)
            b,g,r = cv2.split(res)
            b_avg = mean(b[b>0])
            g_avg = mean(g[g>0])
            r_avg = mean(r[r>0])
            obj._color = b_avg, g_avg, r_avg
        
        if self._selectBiggests.value: self._objectsFound = OTPSelectBiggerBlobs.process(self, self._objectsFound)
            
        ################################################################
        ################################################################

        contours2Display = []
        for obj in self._objectsFound:  contours2Display.append( obj._contour )

        if self._editMode.value: cv2.drawContours( frame, array(contours2Display), -1, (0, 255, 0), 2 )
        else: cv2.drawContours( frame, array(contours2Display), -1, (0, 255, 0), 2 )

        for i, obj in enumerate(self._objectsFound):
            cv2.circle(frame, obj._centroid, 5, (255,0,0), thickness=1)
            p = obj._bounding[0]
            text = "AREA: %d" % obj._area
            cv2.putText(frame, text, p , cv2.FONT_HERSHEY_SIMPLEX, 0.3, (255, 255, 255),  3)
            cv2.putText(frame, text, p , cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255),         1)


        if self._editMode.value:
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
            return frame




    def exportCodeTo(self, folder):
        files_to_copy = []
        files_to_include = []
        constructor = ""
        parameters = []
        imports = ""

        files, imp, cons, params = self._video.value.exportCodeTo(folder)
        constructor += cons
        parameters += params
        imports += imp
        files_to_include += files
        print files_to_include, files
        
        if self._removeBg.value: 
            files, imp, cons, params = self._background.value.exportCodeTo(folder)
            constructor += cons
            parameters += params
            files_to_copy.append( "OTPRemoveBackground" )
            imports += imp
            files_to_include += files

            parameters.append("self._param_background_threshold = %d " % self._threshold.value )


        files_to_copy.append( "OTPColorFilter" )
        
        parameters.append("self._param_color_domain = %d " % self._colorDomain.value )
        parameters.append("self._param_filter_algorithm = '%s' " % self._textAlgo.value )
        parameters.append("self._param_a_min = %d " % self._minR.value )
        parameters.append("self._param_a_max = %d " % self._maxR.value )
        parameters.append("self._param_b_min = %d " % self._minG.value )
        parameters.append("self._param_b_max = %d " % self._maxG.value )
        parameters.append("self._param_c_min = %d " % self._minB.value )
        parameters.append("self._param_c_max = %d " % self._maxB.value )

        if self._useBlur.value: 
            files_to_copy.append( "OTPBlur" )
            parameters.append("self._param_kernel_size = %d " % self._kernelSize.value )
            parameters.append("self._param_blur_threshould = %d " % self._blurThreshold.value )
        

        self._objectsFound = files_to_copy.append( "OTPFindBlobs" )
        parameters.append("self._param_min_area = %d " % self._minArea.value )
        parameters.append("self._param_max_area = %d " % self._maxArea.value )

        if self._selectBiggests.value: 
            files_to_copy.append( "OTPSelectBiggerBlobs" )
            parameters.append("self._param_n_blobs = %d " % self._howMany.value )
        
        for file_to_copy in files_to_copy:
            filename = file_to_copy+".py"
            originalfilepath = tools.getFileInSameDirectory(__file__, filename)
            destinyfilepath = os.path.join( folder, filename )
            #shutil.copy2(originalfilepath,destinyfilepath)

            f = open(originalfilepath, 'r'); text = f.read(); f.close()
            text = text.replace("from core.controllers.", "from ")
            f = open(destinyfilepath, 'w'); f.write(text); f.close()

            imports += "from %s import %s \n" % (file_to_copy, file_to_copy)

        files_to_include += files_to_copy
        files_to_include.reverse()
        return files_to_include, imports, constructor, parameters