from PyQt4 import uic
import uuid
import os


class OTModule(object):
    """
    Module abstract class implementation
    """

    def __init__(self, name):
        self._unique_id = uuid.uuid1() #: Module name
        self._name      = name         #: Module unique identifier
        
    def save(self, saver):
        """
        Save the module values into the saver variable
        @param saver: Dictionary used to store the module information
        @type saver: Dict
        """
        saver['unique_id']  = self._unique_id
        saver['name']       = self.name
        saver['class']      = self.__class__

    def load(self, loader):
        """
        Load the module values from the loader variable
        @param loader: Dictionary with the stored module information
        @type loader: Dict
        """
        self.name       = loader['name']
        self._unique_id = loader['unique_id']

    def close(self):
        """
        Close the module
        """
        pass


    
    ############################################################################
    ############ Properties ####################################################
    ############################################################################

    @property
    def name(self): return self._name

    @name.setter
    def name(self, value): self._name = value

    ############################################################################
    
    @property
    def uid(self): return self._unique_id
        