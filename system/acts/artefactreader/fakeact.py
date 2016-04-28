from .act import ArtefactReaderAct
from gofed_lib.utils import getScriptDir
import json
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT

class FakeArtefactReaderAct(ArtefactReaderAct):

	def __init__(self):
		ArtefactReaderAct.__init__(self)

	def setData(self, data):
		return ArtefactReaderAct.setData(self, data)

	def getData(self):
		return ArtefactReaderAct.getData(self)

	def execute(self):
		self._artefact = {}
		if self.data["artefact"] == ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT:
			fakedatafile = "%s/fakedata/data.json" % getScriptDir(__file__)
			with open(fakedatafile, "r") as f:
				self._artefact = json.load(f)
			return True
		return False
