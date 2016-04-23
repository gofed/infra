from .act import ArtefactReaderAct
from gofed_lib.utils import getScriptDir
import json

class FakeArtefactReaderAct(ArtefactReaderAct):

	def __init__(self):
		ArtefactReaderAct.__init__(self)

	def setData(self, data):
		return ArtefactReaderAct.setData(self, data)

	def getData(self):
		return ArtefactReaderAct.getData(self)

	def execute(self):
		self._artefact = {}
		return False
