from infra.system.plugins.specdataextractor.extractor import SpecDataExtractor
from gofed_lib.utils import getScriptDir
import json

class FakeSpecDataExtractor(SpecDataExtractor):

	def __init__(self):
		SpecDataExtractor.__init__(self)

	def setData(self, data):
		return SpecDataExtractor.setData(self,data)

	def getData(self):
		return SpecDataExtractor.getData(self)

	def execute(self):
		with open("%s/fakedata/specdata.json" % getScriptDir(__file__), "r") as f:
			data = json.load(f)

		self.commit = data["commit"]
		self.project = data["project"]
		self.ipprefix = data["ipprefix"]
		self.lastupdated = data["lastupdated"]

		return True
