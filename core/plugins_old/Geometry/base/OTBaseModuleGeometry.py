from core.modules.base.OTModulePlugin import OTModulePlugin
from core.modules.formcontrols.OTParamList import OTParamList

class OTBaseModuleGeometry(OTModulePlugin):

	def __init__(self, name, iconFile=None):
		super(OTBaseModuleGeometry, self).__init__(name, iconFile = iconFile)
		self._polygons = OTParamList("Polygons")

	@property
	def polygons(self): return [eval(poly) for name, poly in self._polygons.value]