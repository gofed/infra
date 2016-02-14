import types
import tarfile
import tempfile
import uuid
from shutil import move

class ResourceClient:
	"""Communication with resource provider and retrieve requested resources.

	Every retrieved resource needs to be extracted before provided for processing.
	As client is responsible for extraction, it is responsible for cleaning up.
	Thus, every retrieved resource is extracting into working directory.

	As the working directory is not used as a cache (not yet),
	it is not requered to store its content for a long time.
	Thus, every resource inside the directory which lives longer than
	predefined amount of time can be deleted.
	"""

	def __init__(self, resource_provider, working_directory):
		self.provider = resource_provider
		self.subresource = ""
		self.working_directory = working_directory

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
			# if the provider runs locally, provider is responsible for deleting resource_location
			# if the provider runs remotelly, client is responsible for deleting resource_location

			# resource_location is expected as a tarball
			print resource_location
			# resource_location is read only, don't delete it!!!
			# extract the tarball
			# TODO(jchaloup): catch exceptions for tarfile
			tar = tarfile.open(resource_location)
			dirpath = tempfile.mkdtemp()
			tar.extractall(dirpath)
			rootdir = ""
			for member in tar.getmembers():
				rootdir = member.name.split("/")[0]
				break
			tar.close()

			# move the temp directory under working directory
			resource_dest = "%s/%s_%s%s" % (
				self.working_directory,
				self.__class__.__name__.lower(),
				uuid.uuid4().hex,
				uuid.uuid4().hex
			)
			# TODO(jchaloup): catch exception and raise better one with more info
			move(dirpath, resource_dest)

			self.subresource = "%s/%s" % (resource_dest, rootdir)
			return True

		raise NotImplementedError()

		return False

	def getSubresource(self):
		"""Return location of subresource
		"""
		return self.subresource
