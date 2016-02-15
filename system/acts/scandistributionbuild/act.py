from system.core.meta.metaact import MetaAct
from system.resources.specifier import ResourceSpecifier
from system.resources import types
from system.core.functions.types import FunctionNotFoundError, FunctionFailedError
from system.helpers.schema_validator import SchemaValidator
from system.helpers.utils import getScriptDir
from system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_INFO_FEDORA, ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME
from gofed_lib.helpers import Build
import json

class ScanDistributionBuildAct(MetaAct):

	def __init__(self):
		MetaAct.__init__(
			self,
			"%s/input_schema.json" % getScriptDir(__file__)
		)

		self.exported_api = {}

	def setData(self, data):
		"""Validation and data pre-processing"""
		if not self._validateInput(data):
			return False

		self.product = data["product"]
		self.distribution = data["distribution"]
		self.build = data["build"]["name"]
		self.rpms = data["build"]["rpms"]

		return True

	def getData(self):
		"""Validation and data post-processing"""
		return self.exported_api

	def execute(self):
		"""Impementation of concrete data processor"""

		# parse build's srpm
		srpm = Build(self.build).srpm()
		package = Build(self.build).name()

		# specify resource
		resource = ResourceSpecifier().generateRpm(
			self.product,
			self.distribution,
			self.build,
			srpm,
			subresource = types.SUBRESOURCE_SPECFILE
		)

		data = {
			"product": self.product,
			"distribution": self.distribution,
			"package": package,
			"resource": resource
		}

		data = self.ff.bake("specdataextractor").call(data)

		project = ""
		commit = ""
		ipprefix = ""
		for artefact in data:
			if artefact["artefact"] == ARTEFACT_GOLANG_PROJECT_INFO_FEDORA:
				project = artefact["project"]
				commit = artefact["commit"]
				continue

			if artefact["artefact"] == ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME:
				ipprefix = artefact["ipprefix"]
				continue

		# extract api for each rpm
		for rpm in self.rpms:
			# generate resource specification for rpm
			resource = ResourceSpecifier().generateRpm(
				self.product,
				self.distribution,
				self.build,
				rpm["name"]
			)

			data = {
				"product": self.product,
				"directories_to_skip": rpm["skipped_directories"],
				"distribution": self.distribution,
				"build": self.build,
				"rpm": rpm["name"],
				"resource": resource,
				"project": project,
				"commit": commit,
				"ipprefix": ipprefix
			}

			data = self.ff.bake("distributiongosymbolsextractor").call(data)
			self.exported_api[rpm["name"]] = data

		return True
