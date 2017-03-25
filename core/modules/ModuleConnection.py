from pyforms.Controls import ControlCombo
from pyforms.gui.Controls.ControlBase import ControlBase
from PyQt4 import QtGui, QtCore

class ModuleConnection(ControlCombo):

    def __init__(self,label="",defaultValue="", connecting=None, **kwargs):
        super(ModuleConnection, self).__init__(label, defaultValue, **kwargs)
        self._connectionWith = connecting

        self.form.comboBox.setFocusPolicy(QtCore.Qt.WheelFocus)
        self.form.comboBox.focusInEvent = self.focusInEvent

    def focusInEvent(self, focusEvent):
        super(QtGui.QComboBox, self.form.comboBox).focusInEvent(focusEvent)
        self.updateControl()

    def load(self, data):
        self.updateControl()
        if 'module_unique_id' in data: 
            self.selectModuleByUniqueId( data['module_unique_id'] )
            self.changed_event()

    def save(self, data):
        if self.value!=None: data['module_unique_id'] = self.value._unique_id
        

    def findModule(self, module_unique_id):
        for module in self._items.values():
            if module._unique_id == module_unique_id: return module
        return None

    def updateControl(self):
        for module in self.parent.parentModule.modulesOrdered:
            
            findedModule = self.findModule(module.uid)
            if  module !=self._parent and findedModule==None \
                and isinstance(module, self._connectionWith) and module.isReady():
                self.addItem(str(module.name), module)
            elif findedModule:
                self.updateModuleLabel(findedModule)
       

    def updateModuleLabel(self, module2Find):
        for label, module in self._items.items():
            if module._unique_id == module2Find._unique_id:
                index = self._form.comboBox.findText(label)
                if index>=0:
                    self._form.comboBox.setItemText(index, module.name)
                    self._items.pop( label )
                    self._items[module.name] = module
                break

    def selectModuleByUniqueId(self, module_unique_id):
        module = self.findModule(module_unique_id)
        if module!=None: 
            self.value = module
            
    def currentIndexChanged(self, index):
        if not self._addingItem:
            item = str(self._form.comboBox.currentText())
            if len(item) >= 1:
                print self._items
                ControlBase.value.fset(self, self._items[str(item)])
            self.parent.parentModule.moduleUpdatedEvent( self.parent.parentModule ) # update the viewers
            

    ############################################################################
    ############ Events ########################################################
    ############################################################################

    

    ############################################################################
    ############ Properties ####################################################
    ############################################################################

    @property
    def value(self): 
        if self._value=="": return None
        else: return self._value

    @value.setter
    def value(self, value):
        for key, val in self._items.items():
            if value == val:
                index = self._form.comboBox.findText(key)
                self._form.comboBox.setCurrentIndex(index)
                if self._value!=value: self.changed_event()
                self._value = val
        self.parent.parentModule.moduleUpdatedEvent( self.parent.parentModule ) # update the viewers


    