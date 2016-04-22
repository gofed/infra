from infra.system.helpers.artefact_schema_validator import ArtefactSchemaValidator
import logging
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API
)
from .extractor import DistributionGoSymbolsExtractor
import json

from gofed_lib.utils import getScriptDir

class FakeDistributionGoSymbolsExtractor(DistributionGoSymbolsExtractor):

	def __init__(self):
		DistributionGoSymbolsExtractor.__init__(self)

	def setData(self, data):
		return DistributionGoSymbolsExtractor.setData(self, data)

	def getData(self):
		return DistributionGoSymbolsExtractor.getData(self)

	def execute(self):
		with open("%s/fakedata/packages.json" % getScriptDir(__file__), "r") as f:
			self._packages = json.load(f)

		with open("%s/fakedata/exported_api.json" % getScriptDir(__file__), "r") as f:
			self._exported_api = json.load(f)

		return True
