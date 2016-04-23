from .act import ScanUpstreamRepositoryAct
from gofed_lib.utils import getScriptDir
import json

class FakeScanUpstreamRepositoryAct(ScanUpstreamRepositoryAct):

	def __init__(self):
		ScanUpstreamRepositoryAct.__init__(self)

	def setData(self, data):
		return ScanUpstreamRepositoryAct.setData(self, data)

	def getData(self):
		return ScanUpstreamRepositoryAct.getData(self)

	def execute(self):
		with open("%s/fakedata/info.json" % getScriptDir(__file__), "r") as f:
			self._itemset_info = json.load(f)

		with open("%s/fakedata/commits.json" % getScriptDir(__file__), "r") as f:
			self._items = json.load(f)

		return True
