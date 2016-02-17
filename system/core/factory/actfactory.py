from factory import Factory
from infra.system.helpers.utils import getScriptDir
from infra.system.core.meta.metaact import MetaAct
from infra.system.core.acts.basicact import BasicAct

class ActFactory(Factory):
	"""
	"""

	def __init__(self):
		# TODO(jchaloup): put plugins_dir into config file
		Factory.__init__(
			self,
			"%s/../../acts" % getScriptDir(__file__),
			"infra.system.acts"
		)

	def bake(self, item_ID):
		obj = Factory.bake(self, item_ID)
		if isinstance(obj, MetaAct):
			return BasicAct(obj)

		raise ValueError("act '%s' not bakeable: act kind not supported" % item_ID)
