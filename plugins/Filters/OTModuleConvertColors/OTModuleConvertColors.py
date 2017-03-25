import core.utils.tools as tools, cv2

from core.modules.OTModulePlugin 		import OTModulePlugin
from core.modules.ModuleConnection  	import ModuleConnection
from datatypes.TypeComponentsVideoPipe  import TypeComponentsVideoPipe
from datatypes.TypeColorVideoPipe  			import TypeColorVideoPipe
from datatypes.TypeColorVideo 				import TypeColorVideo


from pyforms.Controls 	import ControlPlayer
from pyforms.Controls  	import ControlCombo
from pyforms.Controls  	import ControlButton


class OTModuleConvertColors(OTModulePlugin,TypeColorVideoPipe):
	

	def __init__(self, name):
		icon_path = tools.getFileInSameDirectory(__file__, 'iconsubbg.jpg')
		TypeColorVideoPipe.__init__(self)
		OTModulePlugin.__init__(self, name,  iconFile=icon_path)

		self._video 		 = ModuleConnection("Video", connecting=TypeColorVideo)
		self._player 		 = ControlPlayer("Video player")
		self._colorDomain 	 = ControlCombo("Color domain")
		
		self._colorDomain.add_item("XYZ",    cv2.COLOR_BGR2XYZ)
		self._colorDomain.add_item("YCrCb",  cv2.COLOR_BGR2YCR_CB)
		self._colorDomain.add_item("HSV",    cv2.COLOR_BGR2HSV)
		self._colorDomain.add_item("HLS",    cv2.COLOR_BGR2HLS)
		self._colorDomain.add_item("Lab",    cv2.COLOR_BGR2LAB)
		self._colorDomain.add_item("Luv",    cv2.COLOR_BGR2LUV)

		self._colorDomain.changed_event = self._player.refresh
		self._video.changed_event 	  = self.newVideoInputChoosen
		self._player.process_frame_event = self.processFrame

		self._formset = [ 
				'_video',
				'_colorDomain',
				"_player",
			]
	
	def newVideoInputChoosen(self):
		ModuleConnection.changed_event(self._video)
		value = self._video.value
		if value:
			self.open(value)
			self._player.value = value
			
	def processFrame(self, frame):
		
		return cv2.cvtColor(frame, self._colorDomain.value)
