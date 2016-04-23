from .act import GoExportedApiDiffAct
from gofed_lib.utils import getScriptDir
import json

class FakeGoExportedApiDiffAct(GoExportedApiDiffAct):

	def __init__(self):
		GoExportedApiDiffAct.__init__(self)

	def setData(self, data):
		return GoExportedApiDiffAct.setData(self, data)

	def getData(self):
		return GoExportedApiDiffAct.getData(self)

	def execute(self):
		with open("%s/fakedata/diff.json" % getScriptDir(__file__), "r") as f:
			self._api_diff = json.load(f)

		return True
