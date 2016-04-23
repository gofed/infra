from .artefactdriver import ArtefactDriver

class FakeArtefactDriver(ArtefactDriver):

	def __init__(self, working_directory, artefact):
		ArtefactDriver.__init__(self, working_directory, artefact)
		self.data = {}

	def store(self, input):
		key = self._generateKey(input)
		self.data[key] = input

	def retrieve(self, data):
		key = self._generateKey(data)
		return self.data[key]

