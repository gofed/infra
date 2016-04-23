from .extractor import RepositoryDataExtractor
from gofed_lib.utils import getScriptDir
import json

class FakeRepositoryDataExtractor(RepositoryDataExtractor):

	def __init__(self):
		RepositoryDataExtractor.__init__(self)

	def setData(self, data):
		return RepositoryDataExtractor.setData(self, data)

	def getData(self):
		return RepositoryDataExtractor.getData(self)

	def execute(self):
		with open("%s/fakedata/repodata.json" % getScriptDir(__file__), "r") as f:
			repodata = json.load(f)

		self.branches = repodata["branches"]
		self.commits = repodata["commits"]

		return True
