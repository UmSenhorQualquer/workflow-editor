from core.plugins.Geometry.base.OTBaseModuleGeometry import OTBaseModuleGeometry
from core.modules.formcontrols.OTControlBase import OTControlBase
from core.modules.formcontrols.OTParamButton import OTParamButton
from core.modules.formcontrols.OTParamSlider import OTParamSlider
from core.modules.formcontrols.OTParamPlayer import OTParamPlayer
from core.modules.formcontrols.OTParamToggle import OTParamToggle
from core.modules.formcontrols.OTParamList import OTParamList
from core.modules.formcontrols.OTParamVideoInput import OTParamVideoInput

from core.utils.tools import createRectanglePoints, createEllipsePoints
import core.utils.tools as tools

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import cv2
import numpy
import pickle

class OTModuleGeometry(OTBaseModuleGeometry):

    def __init__(self, name):
        icon_path = tools.getFileInSameDirectory(__file__, 'icongeo.png')
        OTBaseModuleGeometry.__init__(self,name, iconFile = icon_path)

        self._imgWidth = 0.0
        self._imgHeight = 0.0
        self._startPoint = None
        self._endPoint = None

        self._selectedPoly = None
        self._selectedPoint = None
        

        self._video  = OTParamVideoInput("Video")
        self._player = OTParamPlayer("Video")
        self._remove = OTParamButton("Remove")
        self._square = OTParamToggle("Square")
        self._circle = OTParamToggle("Circle")
        self._export = OTParamButton("Export")
        self._import = OTParamButton("Import")

        self._formset = [ '_video',"_player", ("_square", "_circle", " ","_remove"," ", "_export", "_import"), "=", "_polygons" ]

        self._video.valueUpdated = self.videoSelected
        self._square.value = self.square_toggle
        self._circle.value = self.circle_toggle
        self._remove.value = self.remove_clicked
        self._export.value = self.export_clicked
        self._import.value = self.import_clicked
        
        self._player._videoWidget.onDrag = self.onDragInVideoWindow
        self._player._videoWidget.onEndDrag = self.onEndDragInVideoWindow
        self._player._videoWidget.onClick = self.onClickInVideoWindow
        self._player._videoWidget.onDoubleClick = self.onDoubleClickInVideoWindow
        self._player.processFrame = self.processFrame
        
    def export_clicked(self):
        filename = str(QFileDialog.getSaveFileName(self._form, 'Choose a file', '') )
        if filename!="":
            output = open( filename, 'wb')
            pickle.dump( self._polygons.value , output)
            output.close()

    def import_clicked(self):
        filename = str(QFileDialog.getOpenFileName(self._form, 'Choose a file', '') )
        if filename!="":
            pkl_file = open( filename, 'rb'); data = pickle.load(pkl_file); pkl_file.close()
            self._polygons.value = data

    def processFrame(self, frame):
        rows = self._polygons.value
        for objIndex, obj in enumerate(rows):
            try:
                points = eval(obj[1])
                cv2.polylines(frame, [numpy.array(points,numpy.int32)], True, (0,255,0), 1, lineType=cv2.CV_AA)
                
                for pointIndex, point in enumerate( points ):
                    if self._selectedPoint == pointIndex and objIndex==self._selectedPoly:
                        cv2.circle(frame, point, 2, (255,0,0), 1)
                    else:
                        cv2.circle(frame, point, 2, (0,255,0), 1)
            except: pass
            
        if self._startPoint and self._endPoint:
            if self._square.isChecked():
                cv2.rectangle(frame, self._startPoint, self._endPoint, (233,44,44), 1 )
            elif self._circle.isChecked() and self._endPoint[0]>self._startPoint[0] and self._endPoint[1]>self._startPoint[1]:
                width = self._endPoint[0]-self._startPoint[0]
                height = self._endPoint[1]-self._startPoint[1]
                center = ( self._startPoint[0] + width/2, self._startPoint[1] + height/2 )
                
                cv2.ellipse( frame, center, (width/2,height/2), 0, 0, 360, (233,44,44), 1 )
                
        return frame

    def selectPoint(self,x, y):
        rows = self._polygons.value
        for objIndex, obj in enumerate(rows):
            try:
                points = eval(obj[1])
                for pointIndex, point in enumerate( points):
                    mouseCoord = ( x, y )
                    if tools.pointsDistance( mouseCoord, point ) <= 5:
                        self._selectedPoint = pointIndex
                        self._selectedPoly = objIndex
                        return
                self._selectedPoint = None
                self._selectedPoly = None
            except: pass

    def getIntersectionPoint(self, testPoint, point1, point2, tolerance = 5):
        vector = ( point2[0]-point1[0], point2[1]-point1[1] )
        p0 = point1
        if vector[0]!=0:
            k = float(testPoint[0] - p0[0]) / float(vector[0])
            y = float(p0[1]) + k * float(vector[1]) 
            if point2[0]>point1[0]:
                maxValue = point2[0]
                minValue = point1[0]
            else:
                maxValue = point1[0]
                minValue = point2[0]
            if abs(y-testPoint[1])<=tolerance and testPoint[0]<=maxValue and testPoint[0]>=minValue: return testPoint
            else: return None
        elif vector[1]!=0:
            k = float(testPoint[1] - p0[1]) / float(vector[1])
            x = float(p0[0]) + k * float(vector[0])
            if point2[1]>point1[1]: 
                maxValue = point2[1]
                minValue = point1[1]
            else:
                maxValue = point1[1]
                minValue = point2[1]
            if abs(x-testPoint[0])<=tolerance and testPoint[1]<=maxValue and testPoint[1]>=minValue: return testPoint
            else: return None
        else: return None

    def onDoubleClickInVideoWindow(self, event, x, y):
        mouse = ( int(x*self._imgWidth), int(y*self._imgWidth) )
        rows = self._polygons.value
        for objIndex, obj in enumerate(rows):
            try:
                points = eval(obj[1])
                n_points = len(points)
                for pointIndex, point in enumerate( points ):
                    next_point = points[ (pointIndex+1) % n_points ]
                    intersection = self.getIntersectionPoint(mouse, point, next_point )
                    if intersection != None:
                        self._selectedPoly = objIndex
                        points.insert( pointIndex + 1, intersection )
                        self._polygons.setValue( 1, self._selectedPoly, points )
                        self._selectedPoint = pointIndex + 1
                        return
            except: pass

    
    def onClickInVideoWindow(self, event, x, y):
        self.selectPoint( int(x * self._imgWidth), int(y * self._imgWidth) )

    def onDragInVideoWindow(self, startPoint, endPoint):
        self._startPoint = ( int(startPoint[0] * self._imgWidth), int(startPoint[1] * self._imgWidth) )
        self._endPoint = ( int(endPoint[0] * self._imgWidth), int(endPoint[1] * self._imgWidth) )

        if self._selectedPoly!=None and self._selectedPoint!=None:
            poly = self._polygons.getValue( 1, self._selectedPoly )
            try:
                points = eval(poly)
                points[self._selectedPoint] = self._endPoint
                self._polygons.setValue( 1, self._selectedPoly, points )
            except: pass

        if not self._player.isPlaying(): self._player.refresh() 
            
    def onEndDragInVideoWindow(self, startPoint, endPoint):
        self._startPoint = ( int(startPoint[0] * self._imgWidth), int(startPoint[1] * self._imgWidth) )
        self._endPoint = ( int(endPoint[0] * self._imgWidth), int(endPoint[1] * self._imgWidth) )

        points = None
        if self._square.isChecked():
            points = createRectanglePoints(self._startPoint, self._endPoint)
        elif self._circle.isChecked() and self._endPoint[0]>self._startPoint[0] and self._endPoint[1]>self._startPoint[1]:
            points = createEllipsePoints(self._startPoint, self._endPoint)

        if points: self._polygons += ["Poly_%d" % self._polygons.count, points]

        self._startPoint = None
        self._endPoint = None
        self._square.uncheck()
        self._circle.uncheck()

    def videoSelected(self, value):
        if value and value!="" and value.hasVideo():
            self._player.value = value
            self._imgWidth = float(value.width)
            self._imgHeight = float(value.height)
        else:
            self._player.value = None

    def square_toggle(self, checked):
        if checked:
            self._circle.uncheck()

    def circle_toggle(self, checked):
        if checked:
            self._square.uncheck()

    def remove_clicked(self):
        self._polygons -= -1 #Remove the selected row