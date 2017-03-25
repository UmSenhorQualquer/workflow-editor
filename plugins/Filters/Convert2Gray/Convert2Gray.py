import core.utils.tools as tools, cv2

from core.modules.OTModulePlugin 		import OTModulePlugin
from core.modules.ModuleConnection  	import ModuleConnection
from datatypes.TypeComponentsVideoPipe  import TypeComponentsVideoPipe
from datatypes.TypeColorVideoPipe  			import TypeColorVideoPipe
from datatypes.TypeColorVideo 				import TypeColorVideo


from pyforms.Controls 	import ControlPlayer
from pyforms.Controls  	import ControlCombo
from pyforms.Controls  	import ControlButton


class Convert2Gray(OTModulePlugin,TypeColorVideoPipe):
	

	def __init__(self, name):
		icon_path = tools.getFileInSameDirectory(__file__, 'iconsubbg.jpg')
		OTModulePlugin.__init__(self, name,  iconFile=icon_path)
		TypeColorVideoPipe.__init__(self)

		self._video 		 = ModuleConnection("Video", connecting=TypeColorVideo)
		self._player 		 = ControlPlayer("Video player")
		
		self._video.changed 	  = self.newVideoInputChoosen
		self._player.processFrame = self.processFrame

		self._formset = [ 
				'_video',
				"_player",
			]
	
	def newVideoInputChoosen(self):
		ModuleConnection.changed_event(self._video)
		value = self._video.value
		if value:
			self.open(value)
			self._player.value = value
			
	def processFrame(self, frame):
		return cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
