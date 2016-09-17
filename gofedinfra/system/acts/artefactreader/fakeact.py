from .act import ArtefactReaderAct
from gofedlib.utils import getScriptDir
import json
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT,
	ARTEFACT_GOLANG_IPPREFIX_TO_RPM,
	ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES
)
import os

class FakeArtefactReaderAct(ArtefactReaderAct):

	def __init__(self):
		ArtefactReaderAct.__init__(self)

	def setData(self, data):
		return ArtefactReaderAct.setData(self, data)

	def getData(self):
		return ArtefactReaderAct.getData(self)

	def execute(self):
		self._artefact = {}
		if self.data["artefact"] == ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT:
			fakedatafile = "%s/fakedata/data.json" % getScriptDir(__file__)
			with open(fakedatafile, "r") as f:
				self._artefact = json.load(f)
			return True

		if self.data["artefact"] == ARTEFACT_GOLANG_IPPREFIX_TO_RPM:
			fakedatadir = "%s/fakedata/ipprefixes/rawhide" % getScriptDir(__file__)
			for dirName, subdirList, fileList in os.walk(fakedatadir):
				if dirName.endswith("rawhide"):
					continue

				with open("%s/data.json" % (dirName), "r") as f:
					artefact = json.load(f)
					if artefact["ipprefix"] == self.data["ipprefix"]:
						self._artefact = artefact
						return True

		if self.data["artefact"] == ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT:
			fakedatafile = "%s/fakedata/commit.json" % getScriptDir(__file__)
			with open(fakedatafile, "r") as f:
				self._artefact = json.load(f)
				self._artefact["commit"] = self.data["commit"]
			return True

		if self.data["artefact"] == ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES:
			fakedatadir = "%s/fakedata/distributionpackages" % getScriptDir(__file__)
			for dirName, subdirList, fileList in os.walk(fakedatadir):
				if fileList != ["data.json"]:
					continue

				with open("%s/data.json" % (dirName), "r") as f:
					artefact = json.load(f)
					if artefact["rpm"] == self.data["rpm"]:
						self._artefact = artefact
						return True

		return False
