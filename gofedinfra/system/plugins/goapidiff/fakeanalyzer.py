from .analyzer import GoApiDiff
import json
from gofedlib.utils import getScriptDir

class FakeGoApiDiff(GoApiDiff):

	def __init__(self):
		GoApiDiff.__init__(self)

	def setData(self, data):
		with open("%s/fakedata/api1.json" % getScriptDir(__file__), "r") as f:
			api1 = json.load(f)

		with open("%s/fakedata/api2.json" % getScriptDir(__file__), "r") as f:
			api2 = json.load(f)

		return GoApiDiff.setData(self, {
			"exported_api_1": api1,
			"exported_api_2": api2
		})

	def getData(self):
		return GoApiDiff.getData(self)

	def execute(self):
		return GoApiDiff.execute(self)
