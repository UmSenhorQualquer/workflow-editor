from core.modules.formcontrols.OTParamPositions import OTParamPositions
from core.modules.formcontrols.OTParamGeometry import OTParamGeometry
from core.modules.formcontrols.OTParamDBQuery import OTParamDBQuery
from core.modules.formcontrols.OTParamButton import OTParamButton
from core.modules.formcontrols.OTParamProgress import OTParamProgress
from core.modules.formcontrols.OTParamToggle import OTParamToggle
from core.modules.formcontrols.OTParamSlider import OTParamSlider
from core.modules.formcontrols.OTParamTextArea import OTParamTextArea
from core.modules.formcontrols.OTParamVideoInput import OTParamVideoInput
from core.modules.formcontrols.OTParamPlayer import OTParamPlayer

import core.utils.tools as tools
from core.plugins.OTModuleResultsPlugin.OTModuleResultsPlugin import OTModuleResultsPlugin
from core.modules.modulestypes.OTModulePositions import OTModulePositions
from core.utils.tools import point_inside_polygon

from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from PyQt4 import QtSql
import cv2
from numpy import *
import math



class EnergeticObject(object):



    def __init__(self, row, lastEnergeticObject=None, label=None):
        
        self._rowid, self._frame, self._seconds, self._milliseconds, self._x, self._y, self._blob, self._r, self._g, self._b = row
        self._position = float(self._x), float(self._y)

        if lastEnergeticObject!=None: 
            self._label = lastEnergeticObject._label
            self.calcEnergyProperties(lastEnergeticObject)
        else: 
            self._label = -1
            self._velocity = 0, 0
            self._accelaration = 0, 0

        if label!=None: self._label = label

        self._saved = False
        
    def calcEnergyProperties(self, obj):        
        self._velocity = self._position[0]-obj._position[0],  self._position[1]-obj._position[1]
        self._accelaration = self._velocity[0]-obj._velocity[0],  self._velocity[1]-obj._velocity[1]


    def scorePosition(self, futurePosition, t=1.0):
        x = self._position[0] + self._velocity[0]*t + 0.5*self._accelaration[0]*(t**2)
        y = self._position[1] + self._velocity[1]*t + 0.5*self._accelaration[1]*(t**2)
        predictedPosition = x,y
        #distanceFromOrigin = tools.pointsDistance( predictedPosition,  self._position)
        distance = tools.pointsDistance( predictedPosition,  futurePosition)
        if distance==0: return 1
        return 1 / distance

    def genNextFrame(self):
        new = EnergeticObject( [self._rowid, self._frame+1, 0, 0, self._x, self._y, self._blob, self._r, self._g, self._b] )
        new._accelaration = self._accelaration
        new._velocity = self._velocity
        new._position = self._position
        new._label = self._label
        return new

    def __unicode__(self): return str(self._label)
    def __repr__(self): return str(self._label)
    def __str__(self): return str(self._label)




class OTModuleClusterObjectsPositions(OTModuleResultsPlugin, OTModulePositions):

    def __init__(self, name):
        icon_path = tools.getFileInSameDirectory(__file__, 'icon.jpg')
        OTModuleResultsPlugin.__init__(self, name, iconFile = icon_path)

        self._positions = OTParamPositions("Positions")
        self._video = OTParamVideoInput("Video")
        self._player = OTParamPlayer("Video player")
        self._nobjects = OTParamSlider("Number of objects to track", 1, 1, 10)
        self._run = OTParamButton("Run")
        self._apply = OTParamButton("Apply changes")
        self._progress = OTParamProgress()

        #self._query.readOnly = True
        self._run.value = self.run
        self._apply.value = self.apply
        self._video.valueUpdated = self.newVideoInputChoosen
        self._player.processFrame = self.processFrame
        self._query.form.tableView.keyPressEvent = self.keyPressEvent

        self._current_row = None


        self._formset = [ ('_video',"_positions",'_nobjects','_run') , '_player','=',( "_results", '_apply'),"_query","_progress" ]
        
        self._progress.hide()


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

    def apply(self):
        updatequery = QtSql.QSqlQuery( self.parentModule.sqldb )
        selectquery = QtSql.QSqlQuery( self.parentModule.sqldb )
        query = "SELECT a.object, b.id FROM %s a inner join %s b on a.frame=b.frame and a.new_object=b.object WHERE a.new_object<>'' " % (self._query.table,  self._query.table)
        selectquery.exec_( query )
        while ( selectquery.next() ):
                row = selectquery.record()
                obj           =         int(row.value("object").toString())
                rowid           =         int(row.value("id").toString())
                query = "UPDATE %s SET object=%s WHERE id=%s " % (self._query.table, obj, rowid)
                updatequery.exec_( query )
            
        query = "UPDATE %s SET object=new_object WHERE new_object<>'' " % self._query.table
        updatequery.exec_( query )
        query = "UPDATE %s SET new_object='' " % self._query.table
        updatequery.exec_( query )
        updatequery.finish()
        self._query.orderBy = 1


    def keyPressEvent(self, event): 
        #print event.key()
        if event.key() in (16777235, 16777237, 16777233, 16777232, 16777238, 16777239, 16777248):
            QTableView.keyPressEvent(self._query.form.tableView, event)
        else:
            key = event.text()
            if event.key()==16777219 or event.key()==16777223:  key = ""
            if key=='' or key in self._results.keys:
                for row in self._query.selected_rows_indexes:
                    self._query.setValueIn(row, 13, key)
                self._query.commit()

    def selectionChanged(self, selected, deselected):
        """
        Redefinition of the function selectionChanged from OTModuleResultsPlugin
        """
        QTableView.selectionChanged(self._query.form.tableView, selected, deselected)
        row = self._query.mouseSelectedRow
        if row != None:
            self._current_row = row
            video = self._video.value
            frame_index = int( row[1] )-1
            video.videoInput.setFrame( frame_index )
            self._player.updateFrame()


    def processFrame(self, frame, drawSelectedRows = True):
        """
        This is an event called by the player before he shows the video frame
        @param frame: Frame that would be showed
        @type frame: Numpy array
        """
        #Draw the current mouse selected row
        if self._current_row != None: 
            x           =         int(self._current_row[4])
            y           =         int(self._current_row[5])
            velocity           =         eval(str(self._current_row[6]))
            accelaration    =         eval(str(self._current_row[7]))
            blob      =         array( [eval(str(self._current_row[8]))] )
            
            cv2.circle(frame, (x, y), 6, (0,0,255), -1)
            cv2.polylines( frame, blob, True, (0,255,0), 1 )

            xx = int( math.ceil( x + velocity[0] + 0.5*accelaration[0] ) )
            yy = int( math.ceil( y + velocity[1] + 0.5*accelaration[1] ) )
            cv2.line( frame, (x,y), (xx,yy), (255, 0,0), 2 )

        return frame






    def __smallestDistance(self, point, positions):
        smallest_dist = 1000000
        index = -1
        for i, values in enumerate(positions):
            frame, x, y = int( values[1] ), int( values[4] ), int( values[5] )
            dist = tools.pointsDistance( point, (x,y) )
            if dist<=smallest_dist:
                smallest_dist = dist
                index = i
        return index

    
    def __guessPositions(self, objs_window, nobjects=2):
        origin = [None for x in range(nobjects)]

        for frameIndex, frame in enumerate( objs_window.get()):
            if frameIndex==0: continue
    
            final_selection = list(origin)
            scores = []
            
            for objIndex, obj in enumerate(frame):
                for last_obj in objs_window.get(frameIndex-1):
                    classification = last_obj.scorePosition( obj._position )
                    scores.append( [classification, last_obj, obj] )
            scores = sorted(scores, key=lambda x: x[0], reverse=True)
            
            used = []
            for score_index in range(len(scores)):
                classification, last_object, new_obj = scores[score_index][0], scores[score_index][1], scores[score_index][2]
                #if classification>0.005 and final_selection[last_object._label]==None:
                if final_selection[last_object._label]==None and new_obj not in used:
                    new_obj.calcEnergyProperties(last_object)
                    new_obj._label = last_object._label
                    final_selection[last_object._label] = new_obj
                    used.append(new_obj)
            
            for i, obj in enumerate(final_selection):
                if obj==None: 
                    final_selection[i] = objs_window.get(frameIndex-1)[i].genNextFrame()
            
            objs_window.set(frameIndex, final_selection)

        self._firstTime = False
        return objs_window


    def __getFirstValues(self, query, nvalues):
        sqlquery = QtSql.QSqlQuery( self.parentModule.sqldb )
        sqlquery.exec_(query);
        results = []
        for index in range(nvalues):
            sqlquery.next()
            row = sqlquery.record()

            rowid           =         int(row.value("id").toString())
            frame           =         int(row.value("frame").toString())
            seconds        =        float(row.value("seconds").toString())
            milliseconds  =        float(row.value("milliseconds").toString())
            x =                         int(row.value("x").toString())
            y =                         int(row.value("y").toString())
            obj =                       str(row.value("polygon").toString())
            r =                   str(row.value("r").toString())
            g =                   str(row.value("g").toString())
            b =                   str(row.value("b").toString())

            values = [rowid,frame,seconds,milliseconds,x,y,obj,r,g,b]
            results.append( values )
        return results

    def __row2List(self, row):
        rowid           =         int(row.value("id").toString())
        frame           =         int(row.value("frame").toString())
        seconds        =        float(row.value("seconds").toString())
        milliseconds  =        float(row.value("milliseconds").toString())
        x =                         int(row.value("x").toString())
        y =                         int(row.value("y").toString())
        obj =                       str(row.value("polygon").toString())
        r =                   str(row.value("r").toString())
        g =                   str(row.value("g").toString())
        b =                   str(row.value("b").toString())
        return [rowid, frame, seconds, milliseconds, x, y, obj, r, g, b]
        
    def run(self):
        
        totalResults = self._positions.value.countAllResults()
        self._progress.min = 0
        self._progress.value = 0
        self._progress.max = totalResults
        self._progress.show()
        QApplication.processEvents()

        sqlquery = QtSql.QSqlQuery( self.parentModule.sqldb )
        insertquery = QtSql.QSqlQuery( self.parentModule.sqldb )

        insertquery.exec_("PRAGMA cache_size = 65536")
        insertquery.exec_("PRAGMA temp_store = MEMORY")
        insertquery.exec_("PRAGMA journal_mode = OFF")
        insertquery.exec_("PRAGMA synchronous = OFF")

        tablename = "%s_output" % (self.name.replace(" ", "").lstrip('0123456789.') )
        insertquery.exec_("DROP TABLE IF EXISTS %s" % tablename)
        insertquery.exec_("CREATE TABLE if not exists %s(id INTEGER PRIMARY KEY AUTOINCREMENT, frame BIGINT, seconds DOUBLE, milliseconds BIGINT, x INTEGER, y INTEGER, velocity TEXT, accelaration TEXT, polygon TEXT, r INTEGER, g INTEGER, b INTEGER, object INTEGER, new_object INTEGER)" % tablename)
        
        count = 0
        

        for query in self._positions.value.getAllQueries():
            last_frame, frame_values = -1, []
            sqlquery.exec_(query);

            valuesWindow = tools.RingBuffer(20)

            while ( sqlquery.next() ):
                row = sqlquery.record() 
                values = self.__row2List(row)
                frame = values[1]
                                
                if frame!=last_frame and last_frame!=-1:

                    #first frame give names to objects
                    if valuesWindow.count()==0: valuesWindow.append( [EnergeticObject(vals, label=i) for i, vals in enumerate(frame_values)] )
                    else: valuesWindow.append( [EnergeticObject(vals) for vals in frame_values] )
                    #valuesWindow.printValues()

                    valuesWindow = self.__guessPositions( valuesWindow )
                    
                    if valuesWindow.count()==20:
                        for frameObjects in valuesWindow.get(): 
                            for obj in frameObjects: 
                                if obj._saved!=True:
                                    query = "INSERT INTO %s(frame, seconds, milliseconds, x, y, velocity, accelaration, polygon, r, g, b, object) VALUES (%s,%f,%f,%s,%s,'%s', '%s','%s', %s, %s, %s, %s)" % (tablename, obj._frame, obj._milliseconds, obj._seconds, obj._position[0], obj._position[1], obj._velocity, obj._accelaration, obj._blob, obj._r, obj._g, obj._b, obj._label )
                                    insertquery.exec_( query )
                                    obj._saved = True
                    frame_values = [ values ]
                else:
                    frame_values.append( values )

                last_frame = frame

                count += 1
                self._progress.value = count
                QApplication.processEvents()

            for frameObjects in valuesWindow.get(): 
                for obj in frameObjects: 
                    if obj._saved!=True: 
                        query = "INSERT INTO %s(frame, seconds, milliseconds, x, y, velocity, accelaration, polygon, r, g, b, object) VALUES (%s,%f,%f,%s,%s,'%s', '%s','%s', %s, %s, %s, %s)" % (tablename, obj._frame, obj._milliseconds, obj._seconds, obj._position[0], obj._position[1], obj._velocity, obj._accelaration, obj._blob, obj._r, obj._g, obj._b, obj._label )
                        insertquery.exec_( query )




        insertquery.exec_("CREATE INDEX Idx3 ON %s(object, new_object);" % tablename)
        insertquery.finish()
        self._progress.value = totalResults
        QApplication.processEvents()
        self.parentModule.sqldb.commit()
        self._progress.hide()

        self._results.clearItems()

        for label in range(self._nobjects.value):
            self._results.addItem("%s" % label, "SELECT id, frame, seconds, milliseconds, x, y, velocity, accelaration, object, r, g, b, object, new_object FROM %s WHERE object like %d" % ( tablename, label ) )



    def getArenaIntersection(self, x, y, arenasDict):
        for name, arena in arenasDict:
            contour = array( [eval(arena)] ,int32)
            point = (x,y)
            res = cv2.pointPolygonTest( contour, point, False )
            if res>=0:
                return name
        return "None"