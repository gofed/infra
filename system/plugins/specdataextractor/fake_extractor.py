from system.core.meta.metaprocessor import MetaProcessor
from system.helpers.artefact_schema_validator import ArtefactSchemaValidator
import logging
from system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME,
	ARTEFACT_GOLANG_PROJECT_INFO_FEDORA,
	ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME
)
class FakeSpecDataExtractor(MetaProcessor):

	def __init__(self):
		self.distribution = "f23"
		self.product = "Fedora"
		self.package = "etcd"

		self.project = "github.com/coreos/etcd"
		self.commit = "729b530c489a73532843e664ae9c6db5c686d314"
		self.lastupdated = "2015-12-12"
		self.ipprefix = "github.com/coreos/etcd"

	def setData(self, data):
		return True

	def getData(self):
		"""Validation and data post-processing"""
		data = []

		data.append(self._generateGolangProjectInfoFedora())
		validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_INFO_FEDORA)
		if not validator.validate(data[0]):
			logging.error("%s is not valid" % ARTEFACT_GOLANG_PROJECT_INFO_FEDORA)
			return {}

		data.append(self._generateGolangProjectToPackageName())
		validator = ArtefactSchemaValidator(ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME)
		if not validator.validate(data[1]):
			logging.error("%s is not valid" % ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME)
			return {}

		data.append(self._generateGolangIPPrefixToPackageName())
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
		artefact["package"] = self.package

		return artefact

	def _generateGolangIPPrefixToPackageName(self):
		artefact = {}

		artefact["artefact"] = ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME

		artefact["product"] = self.product
		artefact["distribution"] = self.distribution
		artefact["ipprefix"] = self.project
		artefact["package"] = self.package

		return artefact

	def execute(self):
		return True
