import core.utils.tools as tools, cv2

from pyforms.Controls   import ControlPlayer
from pyforms.Controls   import ControlCombo
from pyforms.Controls   import ControlSlider

from core.modules.ModuleConnection  import ModuleConnection
from datatypes.TypeSingleChannelImage        import TypeSingleChannelImage
from datatypes.TypeBWVideoPipe            import TypeBWVideoPipe
from core.modules.OTModulePlugin    import OTModulePlugin


class OTModuleColorRangeFilter(OTModulePlugin,TypeSingleChannelImage):
    

    def __init__(self, name):
        icon_path = tools.getFileInSameDirectory(__file__, 'iconsubbg.jpg')
        OTModulePlugin.__init__(self, name,  iconFile=icon_path)
        TypeSingleChannelImage.__init__(self)

        self._video     = ModuleConnection("Video", connecting=TypeBWVideoPipe)
        self._player    = ControlPlayer("Video player")

        self._min = ControlSlider("Min", 1, 0, 255)
        self._max = ControlSlider("Max", 255, 0, 255)
        
        self._formset = [ 
                '_video',
                "_player",
                '_min',
                '_max'
            ]
        
        self._player.process_frame_event   = self.processFrame
        self._video.changed_event         = self.newVideoInputChoosen
        self._min.changed_event           = self._player.refresh
        self._max.changed_event           = self._player.refresh

    def newVideoInputChoosen(self):
        value = self._video.value
        if value:
            self.open(value)
            self._player.value = value

    def processFrame(self, frame):
        filtered = cv2.inRange(frame, self._min.value, self._max.value)
        return filtered