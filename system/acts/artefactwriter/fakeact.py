from .act import ArtefactWriterAct
from gofedlib.utils import getScriptDir
import json

class FakeArtefactWriterAct(ArtefactWriterAct):

	def __init__(self):
		ArtefactWriterAct.__init__(self)

	def setData(self, data):
		return ArtefactWriterAct.setData(self, data)

	def getData(self):
		return ArtefactWriterAct.getData(self)

	def execute(self):
		return True
