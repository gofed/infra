import types
import tarfile
import tempfile

class ResourceClient:

	def __init__(self, resource_provider):
		self.provider = resource_provider
		self.subresource = ""

	def _validate(self):
		"""Validate descriptor
		"""
		raise NotImplementedError

	def retrieve(self, descriptor):
		"""Retrieve subresource specified in descriptor
		"""
		# self._validate()
		print descriptor
		if descriptor["resource"] == types.RESOURCE_USER_DIRECTORY:
			# No need to download and extract the directory
			# It is located on a host
			if descriptor["location"].startswith("file://"):
				if descriptor["resource-type"] == types.RESOURCE_TYPE_DIRECTORY:
					# TODO(jchaloup): check if the directory exists
					self.subresource = descriptor["location"][7:]
					return True
				# Extract the directory
				#elif self.descriptor["resource-type"] == types.RESOURCE_TYPE_TARBALL:
		elif descriptor["resource"] == types.RESOURCE_UPSTREAM_SOURCE_CODES:
			provider = self.provider.buildGithubSourceCodeProvider()
			# TODO(jchaloup): catch exceptions from provide(...)
			resource_location =  provider.provide(descriptor["project"], descriptor["commit"])
			# resource_location is expected as a tarball
			print resource_location
			# resource_location is read only, don't delete it!!!
			# extract the tarball
			tar = tarfile.open(resource_location)
			dirpath = tempfile.mkdtemp()
			tar.extractall(dirpath)
			rootdir = ""
			for member in tar.getmembers():
				rootdir = member.name.split("/")[0]
				break
			tar.close()
			# return directory
			print dirpath
			self.subresource = "%s/%s" % (dirpath, rootdir)
			# TODO(jchaloup): once the plugins ends, it must delete the directory
			return True

		raise NotImplementedError()

		return False

	def getSubresource(self):
		"""Return location of subresource
		"""
		return self.subresource
