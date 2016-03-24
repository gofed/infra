from infra.system.resources.client import ResourceClient
from infra.system.resources.types import RESOURCE_FIELD, ResourceNotFoundError
from .types import FunctionFailedError
from gofed_resources.proposal.providerbuilder import ProviderBuilder
import copy

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
		m_data = copy.deepcopy(data)
		# retrieve resource from resource client
		if RESOURCE_FIELD in data:
			# TODO(jchaloup): get client from client builder
			client = ResourceClient(ProviderBuilder(), "/var/lib/gofed/resource_client")
			try:
				client.retrieve(data[RESOURCE_FIELD]):
			except ValueError as e:
				raise ResourceNotFoundError("Unable to retrieve resource '%s': %s" % (data[RESOURCE_FIELD], e))

			m_data[RESOURCE_FIELD] = client.getSubresource()

		if not self.obj.setData(m_data):
			raise FunctionFailedError("Unable to set data")

		if not self.obj.execute():
			raise FunctionFailedError("Computation failed")

		return self.obj.getData()
