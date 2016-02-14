from system.resources.client import ResourceClient
from system.resources.types import RESOURCE_FIELD, ResourceNotFoundError
from types import FunctionFailedError
from gofed_resources.proposal.providerbuilder import ProviderBuilder

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
			# TODO(jchaloup): get client from client builder
			client = ResourceClient(ProviderBuilder(), "/var/lib/gofed/resource_client")
			if not client.retrieve(data[RESOURCE_FIELD]):
				raise ResourceNotFoundError("Unable to retrieve resource: %s" % data[RESOURCE_FIELD])

			data[RESOURCE_FIELD] = client.getSubresource()

		if not self.obj.setData(data):
			raise FunctionFailedError("Unable to set data")

		if not self.obj.execute():
			raise FunctionFailedError("Computation failed")

		return self.obj.getData()
