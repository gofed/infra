import types

class ResourceClient:

	def __init__(self, resource_descriptor):
		self.descriptor = resource_descriptor
		self.subresource = ""

	def _validate(self):
		"""Validate descriptor
		"""
		raise NotImplementedError

	def retrieve(self):
		"""Retrieve subresource specified in descriptor
		"""
		# self._validate()
		if self.descriptor["resource"] == types.RESOURCE_USER_DIRECTORY:
			# No need to download and extract the directory
			# It is located on a host
			if self.descriptor["location"].startswith("file://"):
				if self.descriptor["resource-type"] == types.RESOURCE_TYPE_DIRECTORY:
					# TODO(jchaloup): check if the directory exists
					self.subresource = self.descriptor["location"][7:]
					return True
				# Extract the directory
				#elif self.descriptor["resource-type"] == types.RESOURCE_TYPE_TARBALL:
		return False

	def getSubresource(self):
		"""Return location of subresource
		"""
		return self.subresource
