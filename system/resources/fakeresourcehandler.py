from .client import ResourceHandler
import os
from gofedresources.fake.providerbuilder import FakeProviderBuilder

class FakeResourceHandler(ResourceHandler):

	def __init__(self, resource_provider, working_directory):
		ResourceHandler.__init__(self, FakeProviderBuilder(), working_directory)

	def mkdtemp(self):
		return "tempfile/mkdtemp"

	def move(self, src, dest):
		pass

	def uuid(self):
		return "ac811547d12c4b95b51633a24aea1950"

	def extractTarball(self, tarball_location):
		dirpath = self.mkdtemp()
		rootdir = "rootdir"
		return os.path.join(dirpath, rootdir)

	def extractRpm(self, resource_location):
		dirpath = self.mkdtemp()
		return dirpath

