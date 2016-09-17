from .types import *
import tarfile
import tempfile
import uuid
from shutil import move
from gofedlib.utils import runCommand
from gofedlib.distribution.helpers import Build
import os

class ResourceHandler(object):

	def __init__(self, resource_provider, working_directory):
		self.provider = resource_provider
		self.working_directory = working_directory

	def mkdtemp(self):
		return tempfile.mkdtemp()

	def move(self, src, dest):
		move(src, dest)

	def uuid(self):
		return uuid.uuid4().hex

	def extractTarball(self, resource_location):
		# TODO(jchaloup): catch exceptions for tarfile
		tar = tarfile.open(resource_location)
		dirpath = tempfile.mkdtemp()
		tar.extractall(dirpath)
		rootdir = ""
		for member in tar.getmembers():
			rootdir = member.name.split("/")[0]
			break
		tar.close()

		return os.path.join(dirpath, rootdir)

	def extractRpm(self, resource_location):
		# TODO(jchaloup): use python module (e.g. github.com/srossross/rpmfile)
		dirpath = self.mkdtemp()
		cwd = os.getcwd()
		os.chdir(dirpath)
		runCommand("rpm2cpio %s | cpio -idmv" % resource_location)
		os.chdir(cwd)

		return dirpath

	def handleUpstreamSourceCode(self, repository, commit):
		provider = self.provider.buildSourceCodeProvider(repository)
		# TODO(jchaloup): catch exceptions from provide(...)
		resource_location =  provider.provide(repository, commit)
		# if the provider runs locally, provider is responsible for deleting resource_location
		# if the provider runs remotelly, client is responsible for deleting resource_location
		# resource_location is expected as a tarball
		# resource_location is read only, don't delete it!!!
		# extract the tarball
		dest = self.extractTarball(resource_location)
		dirpath = os.path.dirname(dest)
		rootdir = os.path.basename(dest)

		# move the temp directory under working directory
		resource_dest = "%s/%s_%s%s" % (
			self.working_directory,
			self.__class__.__name__.lower(),
			self.uuid(),
			self.uuid()
		)
		# TODO(jchaloup): catch exception and raise better one with more info
		self.move(dirpath, resource_dest)
		return "%s/%s" % (resource_dest, rootdir)

	def handleRpm(self, product, distribution, build, rpm, subresource):
			provider = self.provider.buildRpmProvider()
			# TODO(jchaloup): catch exceptions from provide(...)
			# product, distribution, build, rpm
			resource_location =  provider.provide(product, distribution, build, rpm)

			dirpath = self.extractRpm(resource_location)

			# move the temp directory under working directory
			resource_dest = "%s/%s_%s%s" % (
				self.working_directory,
				self.__class__.__name__.lower(),
				self.uuid(),
				self.uuid()
			)
			# TODO(jchaloup): catch exception and raise better one with more info
			self.move(dirpath, resource_dest)

			if subresource == SUBRESOURCE_SPECFILE:
				return "%s/%s.spec" % (resource_dest, Build(build).name())
			elif subresource == SUBRESOURCE_DIRECTORY_TREE:
				# TODO(jchaloup): return correct directory under /usr/share/gocode/src
				#	src can contain more projects as rpm can ship more source codes
				#	with different ipprefixes.
				return resource_dest

			raise ValueError("Invalid resource specification")

	def handleRepository(self, repository):
		if repository["provider"] in ["github"]:
			provider = self.provider.buildGitRepositoryProvider()
		elif repository["provider"] in ["bitbucket"]:
			provider = self.provider.buildMercurialRepositoryProvider()
		else:
			raise ValueError("Unsupported provider: %s" % repository["provider"])

		# TODO(jchaloup): catch exceptions from provide(...)
		# product, distribution, build, rpm
		resource_location =  provider.provide(repository)

		dest = self.extractTarball(resource_location)
		dirpath = os.path.dirname(dest)
		rootdir = os.path.basename(dest)

		# move the temp directory under working directory
		resource_dest = "%s/%s_%s%s" % (
			self.working_directory,
			self.__class__.__name__.lower(),
			self.uuid(),
			self.uuid()
		)
		# TODO(jchaloup): catch exception and raise better one with more info
		self.move(dirpath, resource_dest)

		# TODO(jchaloup): call git pull/ hg pull on the repository

		return "%s/%s" % (resource_dest, rootdir)

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
		self._subresource = ""

		self._resource_handler = ResourceHandler(resource_provider, working_directory)

	def _validate(self):
		"""Validate descriptor
		"""
		raise NotImplementedError

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
					self._subresource = descriptor["location"][7:]
					return self
				else:
					raise ValueError("resource-type '%s' not supported" % descriptor["resource-type"])
				# Extract the directory
				#elif self.descriptor["resource-type"] == RESOURCE_TYPE_TARBALL:
			raise ValueError("Location protocol not supported. Only file:// currently supported.")
		elif resource_type == RESOURCE_UPSTREAM_SOURCE_CODES:
			self._subresource = self._resource_handler.handleUpstreamSourceCode(descriptor["repository"], descriptor["commit"])
			return self

		elif resource_type == RESOURCE_RPM:
			self._subresource = self._resource_handler.handleRpm(
				descriptor["product"],
				descriptor["distribution"],
				descriptor["build"],
				descriptor["rpm"],
				descriptor["subresource"]
			)
			return self

		elif resource_type == RESOURCE_REPOSITORY:
			self._subresource = self._resource_handler.handleRepository(descriptor["repository"])
			return self

		raise ValueError("ResourceClient: resource type '%s' not implemented" % resource_type)

	def subresource(self):
		"""Return location of subresource
		"""
		return self._subresource
