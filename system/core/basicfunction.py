from system.resources.client import ResourceClient
from system.resources.types import RESOURCE_FIELD

class BasicFunction:
	"""
	Wrapper for basic functions.
	Basic function always works over local resources.
	The wrapper forwards data to particular plugin.
	Thus, input honors plugin's input and output schema.
	"""
	def __init__(self, obj):
		"""Set instance of a plugin. Each class of the instance must implement MetaProcessor class

		:param obj: instance of MetaProcessor class
		:type  obj: obj
		"""
		self.obj = obj

	def call(self, data):
		"""Forward data to correct methods of obj instance

		:type data: data to forward to a plugin
		"""
		# retrieve resource from resource client
		if RESOURCE_FIELD in data:
			client = ResourceClient(data[RESOURCE_FIELD])
			if not client.retrieve():
				# raise Exception
				return {}

			data[RESOURCE_FIELD] = client.getSubresource()

		if not self.obj.setData(data):
			# TODO(jchaloup): raise exception
			return {}

		if not self.obj.execute():
			# TODO(jchaloup): raise exception
			return {}

		return self.obj.getData()
