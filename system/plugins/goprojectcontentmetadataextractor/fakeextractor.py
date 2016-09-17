from .extractor import GoProjectContentMetadataExtractor
from gofedlib.utils import getScriptDir
import json

class FakeGoProjectContentMetadataExtractor(GoProjectContentMetadataExtractor):

	def __init__(self):
		GoProjectContentMetadataExtractor.__init__(self)

	def setData(self, data):
		return GoProjectContentMetadataExtractor.setData(self, data)

	def getData(self):
		return GoProjectContentMetadataExtractor.getData(self)

	def execute(self):
		with open("%s/fakedata/contentmetadata.json" % getScriptDir(__file__), "r") as f:
			self._metadata = json.load(f)

		return True
