from .act import SpecModelDataProviderAct
from gofedlib.utils import getScriptDir
import json

class FakeSpecModelDataProviderAct(SpecModelDataProviderAct):

	def __init__(self):
		SpecModelDataProviderAct.__init__(self)

	def setData(self, data):
		return SpecModelDataProviderAct.setData(self, data)

	def getData(self):
		return SpecModelDataProviderAct.getData(self)

	def execute(self):
		with open("%s/fakedata/packages.json" % getScriptDir(__file__), "r") as f:
			self.golang_project_packages = json.load(f)

		with open("%s/fakedata/metadata.json" % getScriptDir(__file__), "r") as f:
			self.golang_project_content_metadata = json.load(f)

		return True
