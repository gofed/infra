from .act import ScanDistributionPackageAct
from gofed_lib.utils import getScriptDir
import json

class FakeScanDistributionPackageAct(ScanDistributionPackageAct):

	def __init__(self):
		ScanDistributionPackageAct.__init__(self)

	def setData(self, data):
		return ScanDistributionPackageAct.setData(self, data)

	def getData(self):
		return ScanDistributionPackageAct.getData(self)

	def execute(self):
		with open("%s/fakedata/info.json" % getScriptDir(__file__), "r") as f:
			self._itemset_info = json.load(f)

		with open("%s/fakedata/items.json" % getScriptDir(__file__), "r") as f:
			self._items = json.load(f)

		return True
