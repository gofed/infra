from infra.system.core.meta.metaprocessor import MetaProcessor
import logging
from datetime import datetime
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME,
	ARTEFACT_GOLANG_PROJECT_INFO_FEDORA,
	ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME
)
from infra.system.helpers.artefact_schema_validator import ArtefactSchemaValidator
from infra.system.helpers.utils import getScriptDir
from SpecParser import SpecParser

class SpecDataExtractor(MetaProcessor):

	def __init__(self):
		MetaProcessor.__init__(
			self,
			"%s/input_schema.json" % getScriptDir(__file__)
		)

		# received data
		self.specfile = ""
		self.distribution = ""
		self.product = ""
		self.package = ""

		# extracted data
		self.commit = ""
		self.project = ""
		self.ipprefix = ""
		self.lastupdated = ""

	def setData(self, data):
		"""Validation and data pre-processing"""
		if not self._validateInput(data):
			return False

		self.data = data

		self.product = data["product"]
		self.distribution = data["distribution"]
		self.package = data ["package"]
		self.specfile = data["resource"]

		return True

	def getData(self):
		"""Validation and data post-processing"""
		data = []

		data.append(self._generateGolangProjectInfoFedora())
		# TODO(jchaloup): move validation to unit-tests
		validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_INFO_FEDORA)
		if not validator.validate(data[0]):
			logging.error("%s is not valid" % ARTEFACT_GOLANG_PROJECT_INFO_FEDORA)
			return {}

		data.append(self._generateGolangProjectToPackageName())
		# TODO(jchaloup): move validation to unit-tests
		validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME)
		if not validator.validate(data[1]):
			logging.error("%s is not valid" % ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME)
			return {}

		data.append(self._generateGolangIPPrefixToPackageName())
		# TODO(jchaloup): move validation to unit-tests
		validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME)
		if not validator.validate(data[2]):
			logging.error("%s is not valid" % ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME)
			return {}

		return data

	def _generateGolangProjectInfoFedora(self):
		artefact = {}

		artefact["artefact"] = ARTEFACT_GOLANG_PROJECT_INFO_FEDORA

		artefact["distribution"] = self.distribution
		artefact["project"] = self.project
		artefact["commit"] = self.commit
		artefact["last-updated"] = self.lastupdated

		return artefact

	def _generateGolangProjectToPackageName(self):
		artefact = {}

		artefact["artefact"] = ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME

		artefact["product"] = self.product
		artefact["distribution"] = self.distribution
		artefact["project"] = self.project
		artefact["name"] = self.package

		return artefact

	def _generateGolangIPPrefixToPackageName(self):
		artefact = {}

		artefact["artefact"] = ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME

		artefact["product"] = self.product
		artefact["distribution"] = self.distribution
		artefact["ipprefix"] = self.ipprefix
		artefact["name"] = self.package

		return artefact

	def execute(self):
		"""Impementation of concrete data processor"""
		sp = SpecParser(self.specfile)
		if not sp.parse():
			return False

		# RFE(jchaloup): if %commit is not found => log this to special channel
		self.commit = sp.getMacro("commit")
		if self.commit == "":
			logging.error("commit not found")
			return False

		# RFE(jchaloup): if %import_path is not found => log this to special channel
		self.project = sp.getMacro("provider_prefix")
		if self.project == "":
			self.project = sp.getMacro("import_path")
		if self.project == "":
			logging.error("project not found")
			return False

		# RFE(jchaloup): if %import_path is not found => log this to special channel
		self.ipprefix = sp.getMacro("import_path")
		if self.ipprefix == "":
			logging.error("import path prefix not found")
			return False

		# Extract date from changelog and set its format
		header = sp.getLastChangelog().header
		if header == "":
			logging.error("last changelog not found")
			return False
		try:
			# TODO(jchaloup): preprocess the line before converting to date
			date_data = " ".join(header.split('-')[0].split(" ")[:5])
			self.lastupdated = datetime.strptime(date_data,"* %a %b %d %Y").strftime("%Y-%m-%d")
		except ValueError as e:
			logging.error("invalid changelog header format")
			return False

		return True

