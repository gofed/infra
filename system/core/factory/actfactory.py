from factory import Factory
from infra.system.helpers.utils import getScriptDir
from infra.system.core.meta.metaact import MetaAct

class ActFactory(Factory):
	"""
	"""

	def __init__(self):
		# TODO(jchaloup): put plugins_dir into config file
		Factory.__init__(self, "%s/../../acts" % getScriptDir(__file__))

	def bake(self, item_ID):
		obj = Factory.bake(self, item_ID)
		if isinstance(obj, MetaAct):
			return obj

		raise ValueError("act '%s' not bakeable: act kind not supported" % item_ID)
