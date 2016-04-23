from .storagereader import StorageReader
from .fakeartefactdriver import FakeArtefactDriver

class FakeStorageReader(StorageReader):

	def retrieve(self, data):
		return FakeArtefactDriver("", data["artefact"]).retrieve(data)
