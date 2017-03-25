from core.modules.base.OTModulePlugin import OTModulePlugin


from core.modules.formcontrols.OTParamCombo import OTParamCombo
from core.modules.formcontrols.OTParamVideoInput import OTParamVideoInput
from core.modules.formcontrols.OTParamDBQuery import OTParamDBQuery
from core.modules.formcontrols.OTParamButton import OTParamButton
from core.modules.formcontrols.OTParamSlider import OTParamSlider
from core.modules.formcontrols.OTParamPlayer import OTParamPlayer

from PyQt4.QtCore import *
from PyQt4.QtGui import *
#from PyQt4 import QtSql
import core.utils.tools as tools

class OTModuleResultsPlugin(OTModulePlugin):

    def __init__(self, name, iconFile = None):
        OTModulePlugin.__init__(self, name,  iconFile=iconFile)

        self._results = OTParamCombo("List of results")
        self._query = OTParamDBQuery("Result")

        self._formset = [ "_results", "_query" ]

        self._results.valueUpdated = self.newResultChoosen
        self._query.form.tableView.selectionChanged = self.selectionChanged


    def saveContent(self, saver):
        saver['results'] = self._results._items
        OTModulePlugin.saveContent(self,saver)
        

    def loadSavedContent(self, loader):
        if 'results' in loader:
            results = loader['results']
            for key, sql in results.items():
                self._results.addItem(key, sql)
        OTModulePlugin.loadSavedContent(self,loader)
        

    def selectionChanged(self, selected, deselected):
        pass

    def newResultChoosen(self,value):
        
        self._query.value = value
        self._query.orderBy = 1
        
        
    def countAllResults(self):
        query = QtSql.QSqlQuery( self.parentModule.sqldb )
        query.exec_("select count(*) from %s" % self._query._table)
        query.next()
        row = query.record()
        return int(row.value(0).toString())

    def getAllQueries(self):
        return self._results.items

    def getAllResults(self):
        return self._results.values

    def getAllTables(self):
        queries = self.getAllQueries()
        results = {}
        for query in queries:
            tokens = tools.str_split(query.lower(), ["select", "from", "where", "order by"])
            table = tokens[2].strip()
            results[table] = table

        return results.keys()
