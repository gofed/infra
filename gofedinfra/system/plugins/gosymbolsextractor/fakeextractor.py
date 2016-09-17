from .extractor import GoSymbolsExtractor
from gofedlib.utils import getScriptDir
import json

class FakeGoSymbolsExtractor(GoSymbolsExtractor):
	def __init__(self):
		GoSymbolsExtractor.__init__(self)

	def setData(self, data):
		GoSymbolsExtractor.setData(self, data)
		return True

	def getData(self):
		return GoSymbolsExtractor.getData(self)

	def execute(self):
		with open("%s/fakedata/packages.json" % getScriptDir(__file__), "r") as f:
			self._packages = json.load(f)

		with open("%s/fakedata/exported_api.json" % getScriptDir(__file__), "r") as f:
			self._exported_api = json.load(f)

		return True
