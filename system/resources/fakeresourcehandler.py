from .client import ResourceHandler

class FakeResourceHandler(ResourceHandler):

	def __init__(self, resource_provider, working_directory):
		self.provider = resource_provider
		self.working_directory = working_directory

	def handleUpstreamSourceCode(self, project, commit):
		return "fake/sub/resource/directory"

	def handleRpm(self, product, distribution, build, rpm, subresource):
		return "fake/sub/resource/directory"

	def handleRepository(self, repository):
		return "fake/sub/resource/directory"

