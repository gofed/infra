from .act import ScanDistributionBuildAct
from gofedlib.utils import getScriptDir
import json

class FakeScanDistributionBuildAct(ScanDistributionBuildAct):

	def __init__(self):
		ScanDistributionBuildAct.__init__(self)

	def setData(self, data):
		return ScanDistributionBuildAct.setData(self, data)

	def getData(self):
		return ScanDistributionBuildAct.getData(self)

	def execute(self):
		with open("%s/fakedata/packages.json" % getScriptDir(__file__), "r") as f:
			self._packages = json.load(f)

		with open("%s/fakedata/exported_api.json" % getScriptDir(__file__), "r") as f:
			self._exported_api = json.load(f)

		with open("%s/fakedata/mappings.json" % getScriptDir(__file__), "r") as f:
			self._mappings = json.load(f)

		return True
