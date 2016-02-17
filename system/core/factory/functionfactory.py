from factory import Factory
from system.core.functions.basicfunction import BasicFunction
from system.core.functions.storagefunction import StorageFunction
from system.helpers.utils import getScriptDir
from system.core.meta.metaprocessor import MetaProcessor
from system.core.meta.metastoragereader import MetaStorageReader
from system.core.meta.metastoragewriter import MetaStorageWriter

class FunctionFactory(Factory):
	"""
	Factory baking functions

	https://github.com/gofed/infra/issues/10
	"""

	def __init__(self):
		# TODO(jchaloup): put plugins_dir into config file
		Factory.__init__(self, "%s/../../plugins" % getScriptDir(__file__))

	def bake(self, function_ID):
		obj = Factory.bake(self, function_ID)
		if isinstance(obj, MetaProcessor):
			return BasicFunction(obj)
		elif isinstance(obj, MetaStorageReader) or isinstance(obj, MetaStorageWriter):
			return StorageFunction(obj)

		raise ValueError("function %s not bakeable: function kind not supported" % function_ID)
