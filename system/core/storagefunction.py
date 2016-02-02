from system.core.meta.metastoragereader import MetaStorageReader
from system.core.meta.metastoragewritter import MetaStorageWritter

class StorageFunction:
	"""
	Wrapper for storage functions.
	Storage function never works with resources.
	The wrapper forwards data to particular storage plugin.
	"""
	def __init__(self, obj):
		"""Set instance of a plugin.
		Each class of the instance must implement MetaStorageReader or MetaStorageWritter class

		:param obj: instance of MetaStorageReader or MetaStorageWritter class
		:type  obj: obj
		"""
		self.obj = obj

	def call(self, data):
		"""Forward data to correct methods of obj instance

		:type data: data to forward to a plugin
		"""
		if isinstance(self.obj, MetaStorageReader):
			return self.obj.retrieve(data)
		if isinstance(self.obj, MetaStorageWritter):
			return self.obj.store(data)
		# TODO(jchaloup): raise Exception
