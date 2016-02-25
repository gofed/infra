from .types import *
import tarfile
import tempfile
import uuid
from shutil import move
from gofed_lib.utils import runCommand
from gofed_lib.helpers import Build
import os

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

	def _handleUpstreamSourceCode(self, project, commit):
		provider = self.provider.buildGithubSourceCodeProvider()
		# TODO(jchaloup): catch exceptions from provide(...)
		resource_location =  provider.provide(project, commit)
		# if the provider runs locally, provider is responsible for deleting resource_location
		# if the provider runs remotelly, client is responsible for deleting resource_location
		# resource_location is expected as a tarball
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
		return "%s/%s" % (resource_dest, rootdir)

	def _handleRpm(self, product, distribution, build, rpm, subresource):
			provider = self.provider.buildRpmProvider()
			# TODO(jchaloup): catch exceptions from provide(...)
			# product, distribution, build, rpm
			resource_location =  provider.provide(product, distribution, build, rpm)

			# TODO(jchaloup): use python module (e.g. github.com/srossross/rpmfile)
			dirpath = tempfile.mkdtemp()
			cwd = os.getcwd()
			os.chdir(dirpath)
			runCommand("rpm2cpio %s | cpio -idmv" % resource_location)
			os.chdir(cwd)

			# move the temp directory under working directory
			resource_dest = "%s/%s_%s%s" % (
				self.working_directory,
				self.__class__.__name__.lower(),
				uuid.uuid4().hex,
				uuid.uuid4().hex
			)
			# TODO(jchaloup): catch exception and raise better one with more info
			move(dirpath, resource_dest)

			if subresource == SUBRESOURCE_SPECFILE:
				return "%s/%s.spec" % (resource_dest, Build(build).name())
			elif subresource == SUBRESOURCE_DIRECTORY_TREE:
				# TODO(jchaloup): return correct directory under /usr/share/gocode/src
				#	src can contain more projects as rpm can ship more source codes
				#	with different ipprefixes.
				return resource_dest

			raise ValueError("Invalid resource specification")


	def retrieve(self, descriptor):
		"""Retrieve subresource specified in descriptor
		"""
		# self._validate()
		resource_type = descriptor["resource"]
		if resource_type == RESOURCE_USER_DIRECTORY:
			# No need to download and extract the directory
			# It is located on a host
			if descriptor["location"].startswith("file://"):
				if descriptor["resource-type"] == RESOURCE_TYPE_DIRECTORY:
					# TODO(jchaloup): check if the directory exists
					self.subresource = descriptor["location"][7:]
					return True
				# Extract the directory
				#elif self.descriptor["resource-type"] == RESOURCE_TYPE_TARBALL:
		elif resource_type == RESOURCE_UPSTREAM_SOURCE_CODES:
			self.subresource = self._handleUpstreamSourceCode(descriptor["project"], descriptor["commit"])
			return True

		elif resource_type == RESOURCE_RPM:
			self.subresource = self._handleRpm(
				descriptor["product"],
				descriptor["distribution"],
				descriptor["build"],
				descriptor["rpm"],
				descriptor["subresource"]
			)
			return True

		raise NotImplementedError()

		return False

	def getSubresource(self):
		"""Return location of subresource
		"""
		return self.subresource
