
class BaseViewer(object):
    """
    Abstract class that implements the graphical perspectives of the current project
    """
    _project = None #: Current project
    _controller = None #Parent controller

    def __init__(self, controller): 
        self._project = None
        self._controller = controller

    def updateView(self, project):
        """
        Function called to updated project
        @param project: Project object
        @type project: OTModuleProject
        """
        self._project = project

    def saveContent(self, saver):
        """
        Save the BaseViewer values into the saver variable
        @param saver: Dictionary used to store the module information
        @type saver: Dict
        """
        pass

    def loadSavedContent(self, loader):
        """
        Load the BaseViewer values from the loader variable
        @param loader: Dictionary with the stored module information
        @type loader: Dict
        """
        pass