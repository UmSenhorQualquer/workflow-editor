from core.modules.formcontrols.OTParamVideoInput import OTParamVideoInput
from core.modules.formcontrols.OTParamButton import OTParamButton
from core.modules.formcontrols.OTParamSlider import OTParamSlider
from core.modules.formcontrols.OTParamPlayer import OTParamPlayer
from core.modules.formcontrols.OTParamPositions import OTParamPositions
from core.modules.formcontrols.OTParamProgress import OTParamProgress
from core.modules.formcontrols.OTParamCheckBox import OTParamCheckBox
from core.modules.formcontrols.OTParamCheckBoxList import OTParamCheckBoxList
from core.datatypes.video.OTVideoInput import OTVideoInput
from core.modules.formcontrols.OTParamToggle import OTParamToggle
from core.modules.formcontrols.OTParamTextArea import OTParamTextArea

import core.utils.tools as tools
from core.plugins.OTModuleResultsPlugin.OTModuleResultsPlugin import OTModuleResultsPlugin
from core.modules.modulestypes.OTModulePositions import OTModulePositions
from core.modules.formcontrols.OTParamProgress import OTParamProgress

from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from PyQt4.QtSql import *
from numpy import *
import pickle
import math
import time
import cv2

class OTModuleAdjustPositions(OTModuleResultsPlugin, OTModulePositions):

    

    def __init__(self, name):
        icon_path = tools.getFileInSameDirectory(__file__, 'icon.jpg')
        OTModuleResultsPlugin.__init__(self, name, iconFile = icon_path)

        self._x_col = 4 #Indicate the column with the X coord
        self._y_col = 5 #Indicate the column with the Y coord
        self._frame_col = 1 #Indicate the column with the Y coord
        self._object_col = 6
        self._current_row = None

        self._imgWidth = 0.0
        self._imgHeight = 0.0
        self._startPoint = None
        self._endPoint = None

        self._video = OTParamVideoInput("Video")
        self._positions = OTParamPositions("Positions")
        self._showPos = OTParamCheckBox("Show position")
        self._showTrack = OTParamCheckBox("Show track")
        self._trackRange = OTParamSlider("Track range", 10, 10, 1000)
        self._player = OTParamPlayer("Video player")
        self._progress = OTParamProgress()
        
        #Fields used to configure the Position draw function
        self._show_draw_function = OTParamToggle("Show/Hide draw function")
        self._draw_function = OTParamTextArea("Draw function", """def draw(frame, row):
            x, y = int(row[self._x_col]), int(row[self._y_col])
            cv2.circle(frame, (x, y), 3, (0,255,0), thickness=2, lineType= cv2.cv.CV_AA)""")
        self._importFunc = OTParamButton("Import")
        self._exportFunc = OTParamButton("Export")
        
        #Fields used to configure the interpolation
        self._columns = OTParamCheckBoxList("List of columns to interpolate")
        self._run_interpolation = OTParamButton("Interpolate")
        self._run_interpolation_4_all = OTParamButton("Interpolate")

        #organization of the form
        self._formset = [   ('_video','_positions'), 
            [ ('_columns', '_run_interpolation', '_run_interpolation_4_all'),
            "_draw_function", 
            (" ", "_importFunc", "_exportFunc"), 
            "_player",
            ('_showPos',"_showTrack", "_trackRange")
            ,"=","_results", "_query"], '_progress' ]

        self._trackRange.enabled = False
        self._showPos.value = True

        #setting up the fields events
        self._player.processFrame = self.processFrame
        self._video.valueUpdated = self.newVideoInputChoosen
        self._positions.valueUpdated = self.newPositionsChoosen
        self._showTrack.valueUpdated = self.showTrackToggle
        self._query.selectionChanged = self.tableSelectionChanged
        self._trackRange.valueUpdated = self.updateTrackRange
        self._player._videoWidget.onEndDrag = self.onEndDragInVideoWindow
        self._show_draw_function.value = self.showHideDrawFunction
        self._importFunc.value = self.importFunction
        self._exportFunc.value = self.exportFunction
        self._run_interpolation.value = self.interpolationPositions
        self._run_interpolation_4_all.value = self.interpolateAllPositions

        #Hide fields
        self._draw_function.hide()
        self._progress.hide()
        self._importFunc.hide()
        self._exportFunc.hide()
        self._columns.hide()
        self._run_interpolation.hide()
        self._run_interpolation_4_all.hide()
        
        #Configure the popup menu
        self._query.add_popup_menu_option("-")
        self._query.addPopupSubMenuOption("Add", {"Interpolation": self.showColumns4Interpolation, "Duplicate row": self.addDuplicatedRow })
        self._query.add_popup_menu_option("Remove", self._query.remove)
        self._query.add_popup_menu_option("-")
        self._query.add_popup_menu_option("Approximate all positions", self.approximatePositions)
        self._query.add_popup_menu_option("Interpolate all positions", self.showColumns4InterpolationAll)
        
        self._current_row_index = None #Variable used to read the current row when the video is playing

    def onEndDragInVideoWindow(self, startPoint, endPoint, refresh=True):
        self._startPoint = ( int(startPoint[0] * self._imgWidth), int(startPoint[1] * self._imgWidth) )
        self._endPoint = ( int(endPoint[0] * self._imgWidth), int(endPoint[1] * self._imgWidth) )

        current_row = self._query.mouseSelectedRow

        if current_row!=None:
            current_index = self._query.selected_row_index
            current_frame = int(current_row[self._frame_col])
            if (self._player.value.getCurrentFrame()) == current_frame:
                x, y = int(current_row[self._x_col]), int(current_row[self._y_col])
                #print "current_row", self._startPoint, x, y
                    
                if tools.pointsDistance( self._startPoint , (x,y) ) <= 10:
                    self._query.setValueIn( current_index, self._x_col, self._endPoint[0] )
                    self._query.setValueIn( current_index, self._y_col, self._endPoint[1] )
                    self._current_row = self._query.valuesInRow(current_index)
                    if refresh: 
                        self._query.commit()
                        self._player.refresh()
                        self._query.refresh( current_index )
                        self._query.select()

    def exportFunction(self):
        filename = str(QFileDialog.getSaveFileName(self._form, 'Choose a file', '') )
        if filename!="":
            output = open( filename, 'wb')
            pickle.dump( self._draw_function.value , output)
            output.close()

    def importFunction(self):
        filename = str(QFileDialog.getOpenFileName(self._form, 'Choose a file', '') )
        if filename!="":
            pkl_file = open( filename, 'rb'); data = pickle.load(pkl_file); pkl_file.close()
            self._draw_function.value = data
            func = self._draw_function.value
            exec func
            self.drawRow = draw

    def showHideDrawFunction(self, value):
        if value:
            self._player.hide()
            self._importFunc.show()
            self._exportFunc.show()
            self._draw_function.show()
        else:
            self._draw_function.hide()
            self._importFunc.hide()
            self._exportFunc.hide()
            self._player.show()

            func = self._draw_function.value
            #code = compile(func, '<string>', 'exec')
            exec func
            self.drawRow = draw
            

            """d = {}
            exec func.strip() in d
            print d
            setattr(self.__class__, 'drawRow', d['drawRow'])
            """
            #self.drawRow = eval( func)




    def approximatePositions(self):
        totalCountRows = self._query.count
        firstRow = self._query.valuesInRow( totalCountRows-1 )

        firstPoint = ( int(firstRow[self._x_col]), int(firstRow[self._y_col]) )
        lastAngle = None

        self._progress.show()
        self._progress.min = 0
        self._progress.value = 0
        self._progress.max = totalCountRows

        query = QSqlQuery( self.parentModule.sqldb )
        
        self._query.beginTransaction()
        for i in range( totalCountRows-2, 0, -1 ):            #print i
            currentRow = self._query.valuesInRow( i )
            currentPoint = ( int(currentRow[self._x_col]), int(currentRow[self._y_col]) )
            dist = tools.pointsDistance( firstPoint, currentPoint )
            vector = ( firstPoint[0]-currentPoint[0], firstPoint[1]-currentPoint[1] )
            angle = math.atan2( vector[1], vector[0] )
            angleInDegrees = math.degrees( angle )

            frame = currentRow[self._frame_col]
            obj = currentRow[self._object_col]

            #print "angle:---", angleInDegrees, lastAngle
            if lastAngle==None: lastAngle=angleInDegrees
            if dist<=10: 
                #self._query.removeRow( i )
                #print "DELETE FROM %s WHERE frame='%s' and object='%s' " % (self._query.table, frame, obj )
                query.exec_("DELETE FROM %s WHERE frame='%s' and object='%s' " % (self._query.table, frame, obj ) )
            elif( math.fabs(lastAngle-angleInDegrees)>=5 ): 
                #print "angles", angleInDegrees, lastAngle
                firstPoint = currentPoint
                lastAngle = angleInDegrees
            else:
                #print "DELETE FROM %s WHERE frame='%s' and object='%s' " % (self._query.table, frame, obj )
                query.exec_("DELETE FROM %s WHERE frame='%s' and object='%s' " % (self._query.table, frame, obj ) )
                #self._query.removeRow( i )


            self._progress.value = totalCountRows - i
            QApplication.processEvents()

        self._query.commit()
        self._progress.hide()
        self._query.refresh(0)


    def showTrackToggle(self, value):
        self._trackRange.enabled = value
   

    def  updateTrackRange(self, value):
        if isinstance(self._player.value, OTVideoInput): self._player.refresh()
        

    ############################################################################
    ############ Parent class functions reemplementation #######################
    ############################################################################

    def selectionChanged(self, selected, deselected):
        """
        Redefinition of the function selectionChanged from OTModuleResultsPlugin
        """
        QTableView.selectionChanged(self._query.form.tableView, selected, deselected)
        row = self._query.mouseSelectedRow
        if row != None:
            self._current_row = row
            video = self._video.value
            frame_index = int( row[self._frame_col] )
            video.videoInput.setFrame( frame_index-1 )
            self._player.updateFrame()

    ############################################################################
    ############ Events ########################################################
    ############################################################################

    def updateProgressBar(self, index): self._progress.value = index

    def interpolateAllPositions(self):
        """
        Event called when user click in interpolation button
        """
        self._run_interpolation.hide()
        self._run_interpolation_4_all.hide()
        self._columns.hide()        
        self._player.show()
        
        totalCountRows = self._query.count
        n_columns = len(self._query.columns)
        checked_columns = self._columns.checkedIndexes
        cols_2_interpolate = map( lambda x: True if x in checked_columns else False, range(n_columns) )
        
        self._progress.show()
        self._progress.min = 0
        self._progress.value = 0
        self._progress.max = totalCountRows
        
        for i in range( 0, totalCountRows-1 ):
            self.interpolateBetween2Rows( i, i+1, update = self.updateProgressBar ,cols_2_interpolate = cols_2_interpolate )
            self._query.commit()     
            self._progress.value = i
           
        self._progress.hide()
        self._query.orderBy = 1

  

    def interpolationPositions(self):
        """
        Event called when user click in interpolation button
        """
        self._run_interpolation.hide()
        self._run_interpolation_4_all.hide()
        self._columns.hide()        
        self._player.show()

        rowsIndexes = self._query.selected_rows_indexes
        rowsIndexes.sort()
        if len(rowsIndexes)==2 and rowsIndexes[0]==rowsIndexes[1]-1: #check is the rows are consecutives
            rows = self._query.mouseSelectedRows
            diff = float(abs( int(rows[1][0]) - int(rows[0][0]) ))
            if diff > 1 :
                print rowsIndexes[0], rowsIndexes[1] 
                self.interpolateBetween2Rows( rowsIndexes[0], rowsIndexes[1], update = self.updateProgressBar  )
                self._query.commit()
                self._query.orderBy = 1
                self._query.selected_rows_indexes = rowsIndexes[0]
            else:
                QMessageBox. warning(self._form, 'Warning', "Is not possible to add more frames between the selected ones")
        else:
            QMessageBox. warning(self._form, 'Warning', "You should select two consecutive rows")
        

    def addDuplicatedRow(self):
        """
        Event called when a user click on the popup menu option
        """
        rows = self._query.mouseSelectedRows
        rowsIndexes = self._query.selected_rows_indexes
        if len(rows)==1:
            lastRow = rows[-1]
            self._query.addRow(lastRow, rowsIndexes[0])
        else:
            QMessageBox. warning(self._control, 'Warning', "You should select one row to duplicate")
        self._query.orderBy = 1
        self._query.selected_rows_indexes = rowsIndexes[0]

    def showColumns4Interpolation(self):
        """
        Event called when a user click on the popup menu option
        """
        self._player.hide()
        self._draw_function.hide()
        self._exportFunc.hide()
        self._importFunc.hide()
        self._run_interpolation_4_all.hide()

        self._columns.show()
        self._run_interpolation.show()


    def showColumns4InterpolationAll(self):
        """
        Event called when a user click on the popup menu option
        """
        self._player.hide()
        self._draw_function.hide()
        self._exportFunc.hide()
        self._importFunc.hide()
        self._run_interpolation.hide()

        self._columns.show()
        self._run_interpolation_4_all.show()


    def tableSelectionChanged(self):
        """
        Event called when a user select rows using the popup menu
        """
        self._player.refresh()

    def newVideoInputChoosen(self, value):
        """
        Event called when a user select rows using the popup menu
        @param value: Video module
        @type value: OTModule
        """
        OTParamVideoInput.valueUpdated(self._video,value)
        if value.videoInput:
            value.videoInput.setFrame(0)
            self._player.value = value.videoInput
            self._imgWidth = float(value.videoInput.width)
            self._imgHeight = float(value.videoInput.height)            
            self._trackRange.max = value.videoInput.endFrame-value.videoInput.startFrame

    def newPositionsChoosen(self, value):
        """
        Event called when a new dataset of Positions is choosen
        @param frame: Frame that would be showed
        @type frame: Numpy array
        """
        if value:
            items = value._results.values
            self._results.clearItems()
            for key, sql in items: self._results.addItem(key, sql)

            self._columns.clear()
            list_of_columns = self._query.columns
            self._columns.value = map(lambda x: (x, False), list_of_columns)
            
            self._x_col = self._query.columnIndex("x")
            self._y_col = self._query.columnIndex("y")
            self._frame_col = self._query.columnIndex("frame")

    def processFrame(self, frame, drawSelectedRows = True):
        """
        This is an event called by the player before he shows the video frame
        @param frame: Frame that would be showed
        @type frame: Numpy array
        """

        #Draw the path of the rat
        if self._showTrack.value:
            row_index = self._query.selected_row_index
            if row_index!=None:
                points = []
                for row in range(row_index, row_index + self._trackRange.value):
                    values = self._query.valuesInRow(row)
                    if values!= None:
                        x = int(values[self._x_col])
                        y = int(values[self._y_col])
                        points.append( (x,y) )
                if len(points)>0: cv2.polylines( frame , [array(points,int32)] , False, (255,255,0), 1, lineType=cv2.cv.CV_AA )
            

        #draw the selected path
        #When the rows are selected with the popup menu in the Table
        if drawSelectedRows:
            selectedRows = self._query.selectedRows
            if len( selectedRows )>0:
                track_points = []
                for row in selectedRows:
                    values = self._query.valuesInRow(row)
                    x = int(values[self._x_col])
                    y = int(values[self._y_col])
                    track_points.append( (x,y) )
                cv2.polylines(frame, [array(track_points,int32)], False, (0,255,0), 1)
                for point in track_points: cv2.circle(frame, point, 3, (0,0,255), thickness=1, lineType= cv2.cv.CV_AA)


        #Draw the current mouse selected row
        if self._current_row != None  and self._showPos.value: frame = self.drawRow( frame, self._current_row, (0,0,255) )
            
        if self._player.isPlaying(): self.drawCurrentPositionWhenIsPlaying(frame)

        return frame


    ############################################################################
    ############ Functions #####################################################
    ############################################################################

    def search_4_frame(self, frame2Search, startAtRow = 0):
        """
        This function search for a frame in the List _query
        @param frame2Search: Frame to search
        @type frame2Search: Integer
        @param startAtRow: Start looking in the List row index
        @type startAtRow: Integer
        """

        if startAtRow<0: startAtRow=0
        total_count_rows = self._query.count
        
        if total_count_rows==0: # No rows
            return None
        elif total_count_rows==1: #If only one row
            unique_row = self._query.valuesInRow( 0 )
            frame = int(unique_row[self._frame_col])
            if frame > frame2Search: return 0, None, unique_row, None
            else: return None, 0, None, unique_row
        elif startAtRow >= total_count_rows: # In case of start searching in a non existing row
            last_row = self._query.valuesInRow( total_count_rows-1 )
            return total_count_rows-1, None, last_row, None
        else:
            #check the next row
            previous_row    = self._query.valuesInRow( startAtRow )
            next_row        = self._query.valuesInRow( startAtRow + 1 )
            if previous_row!=None and next_row!=None: #check the current row
                previous_frame  = int(previous_row[self._frame_col])
                next_frame      = int(next_row[self._frame_col])
                if previous_frame<=frame2Search<next_frame: 
                    return startAtRow, startAtRow+1, previous_row, next_row
                else: #check the next row
                    previous_row    = self._query.valuesInRow( startAtRow+1 )
                    next_row        = self._query.valuesInRow( startAtRow+2 )
                    if previous_row!=None and next_row!=None:
                        previous_frame  = int(previous_row[self._frame_col])
                        next_frame      = int(next_row[self._frame_col])
                        if previous_frame<=frame2Search<next_frame: 
                            return startAtRow+1, startAtRow+2, previous_row, next_row

            #check if the frame to search is bellow the first row and higher than the last frame
            first_row = self._query.valuesInRow( 0 )
            first_frame = int(first_row[self._frame_col])
            last_row = self._query.valuesInRow( total_count_rows-1 )
            last_frame = int(last_row[self._frame_col])
            if first_frame>=frame2Search: 
                return None, 0, None, first_row
            elif frame2Search>=last_frame:
                return total_count_rows-1, None, last_row, None
            else:
                #Give up!!!! ....Start a binary tree search
                previous_row_index  = 0
                next_row_index      = (total_count_rows+1)/2
                count = 0
                # search for the frame
                calculateSize = True
                while True:
                    if count > 10000: # for security. We don't want the algorithm to enter in a infinite loop
                        return None 
                    if calculateSize: sizeOfList2Search = (next_row_index - previous_row_index)
                    calculateSize = True

                    next_row            = self._query.valuesInRow( next_row_index )
                    next_frame          = int( next_row[self._frame_col] )

                    previous_row        = self._query.valuesInRow( previous_row_index )
                    previous_frame      = int( previous_row[self._frame_col] )

                    if sizeOfList2Search==1 and previous_frame <= frame2Search < next_frame:
                        return previous_row_index, next_row_index, previous_row, next_row
                    elif sizeOfList2Search<1:
                        return None
                    elif previous_frame==frame2Search:
                        return previous_row_index, previous_row_index+1, previous_row, self._query.valuesInRow( previous_row_index+1 )
                    elif next_frame <= frame2Search and sizeOfList2Search>1:
                        previous_row_index = next_row_index
                        next_row_index += (sizeOfList2Search+1)/2
                        if next_row_index>=total_count_rows: next_row_index = total_count_rows-1
                    elif previous_frame < frame2Search < next_frame and sizeOfList2Search>1:
                        next_row_index -= (sizeOfList2Search+1)/2
                        if next_row_index<0: next_row_index = previous_row_index+1
                        calculateSize = False
                    else:
                        count += 1


                
    def drawCurrentPositionWhenIsPlaying( self, frame ):
        current_frame = self._player.value.getCurrentFrame()
        res = self.search_4_frame( current_frame, self._current_row_index )
        
        if res!=None and self._showPos.value:
            previous_index, next_index, previous_row, next_row = res

            row = None
            if previous_row==None:
                self._current_row_index = 0
                row = next_row
                x, y = int(row[self._x_col]), int(row[self._y_col])
            elif next_row==None:
                self._current_row_index = previous_index
                row = previous_row
                x, y = int(row[self._x_col]), int(row[self._y_col])
            else:
                row = previous_row
                prev_x, prev_y = float(previous_row[self._x_col]), float(previous_row[self._y_col])
                next_x, next_y = float(next_row[self._x_col]), float(next_row[self._y_col])
                prev_frame, next_frame = int(previous_row[0]), int(next_row[0])
                nSteps = float(next_frame - prev_frame)
                xStep, yStep = (next_x-prev_x)/nSteps, (next_y-prev_y)/nSteps
                nSteps2CurrentFrame = float(current_frame-prev_frame)
                x, y = xStep*nSteps2CurrentFrame, yStep*nSteps2CurrentFrame
                x, y = int(round( prev_x + x )), int(round( prev_y + y ))

            #row[self._x_col], row[self._y_col] = x, y
            #frame = self.drawRow( frame, row, (255,0,0) )
            cv2.circle(frame, (x,y), 3, (255,0,0), 2)
        return frame


    def drawRow(self, frame, row, color = (0,255,0) ):
        x, y = int(row[self._x_col]), int(row[self._y_col])
        cv2.circle(frame, (x, y), 3, color, thickness=2, lineType= cv2.cv.CV_AA)
        return frame


    def interpolateBetween2Rows(self, row1, row2, update = (lambda x: 0), cols_2_interpolate = None ):
        """
        Interpolate values between 2 rows
        @param row1: First row
        @type row1: Integer
        @param row2: First row
        @type row2: Integer
        """
        if cols_2_interpolate==None:
            checked_columns = self._columns.checkedIndexes
            n_columns = len(self._query.columns)
            cols_2_interpolate = map( lambda x: True if x in checked_columns else False, range(n_columns) )
        else:
            n_columns = len(cols_2_interpolate)
        
        previous_row = self._query.valuesInRow( row1 )
        next_row = self._query.valuesInRow( row2 )    
        previous_frame = int( previous_row[self._frame_col] )
        next_frame = int( next_row[self._frame_col] )
        diff_frames = float( next_frame - previous_frame )
        if diff_frames>1:
            previous, next, diff, step = [], [], [], []
            for i in range(n_columns): 
                if cols_2_interpolate[i]:
                    previous.append(    float(previous_row[i]) )
                    next.append(        float(next_row[i])     )
                    diff = float(next[i]) - float(previous[i])
                    step.append( diff / diff_frames )                        
                else: 
                    step.append( None )
                    previous.append(    previous_row[i] )
                    next.append(        next_row[i]     )

            for j in range(1, int(diff_frames)):
                values = []
                for i in range(n_columns):
                    if cols_2_interpolate[i]:
                        if int(previous[i])==previous[i] and int(next[i])==next[i]:
                            val = int(previous[i]) + int(round( step[i]* float(j) ))
                        else:
                            val = previous[i] + step[i]*float(j)
                    else: val = previous[i]
                    values.append( val )
                update( row1 + j )

                values.pop(0)
                self._query.addRow( values, -1,cols= [ 'frame', 'seconds','milliseconds', 'x', 'y', 'object' ])
                QApplication.processEvents()