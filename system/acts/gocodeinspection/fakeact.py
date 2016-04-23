from .act import GoCodeInspectionAct
from gofed_lib.utils import getScriptDir
import json

class FakeGoCodeInspectionAct(GoCodeInspectionAct):

	def __init__(self):
		GoCodeInspectionAct.__init__(self)

	def setData(self, data):
		return GoCodeInspectionAct.setData(self, data)

	def getData(self):
		return GoCodeInspectionAct.getData(self)

	def execute(self):
		with open("%s/fakedata/packages.json" % getScriptDir(__file__), "r") as f:
			self._golang_project_packages = json.load(f)

		return True
