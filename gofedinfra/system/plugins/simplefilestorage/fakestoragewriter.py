from .storagewriter import StorageWriter
from .fakeartefactdriver import FakeArtefactDriver

class FakeStorageWriter(StorageWriter):

	def store(self, data):
		return FakeArtefactDriver("", data["artefact"]).store(data)
