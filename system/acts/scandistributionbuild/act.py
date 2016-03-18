from infra.system.core.meta.metaact import MetaAct
from infra.system.resources.specifier import ResourceSpecifier
from infra.system.resources import types
from infra.system.helpers.utils import getScriptDir
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECT_INFO_FEDORA,
	ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API
)
from gofed_lib.helpers import Build

class ScanDistributionBuildAct(MetaAct):

	def __init__(self):
		MetaAct.__init__(
			self,
			"%s/input_schema.json" % getScriptDir(__file__)
		)

		self.exported_api = {}
		self.packages = {}

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
		return {
			"exported_api": self.exported_api,
			"packages": self.packages
		}

	def execute(self):
		"""Impementation of concrete data processor"""

		# check storage
		# I can not check for spec file specific macros as I need project
		# to get artefact from a storage. Without the project I can not
		# get artefact from a storage.

		self.exported_api = {}
		self.packages = {}

		missing_rpms = []
		for rpm in self.rpms:
			rpm_name = rpm["name"]
			data = {
				"artefact": ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES,
				"product": self.product,
				"distribution": self.distribution,
				"build": self.build,
				"rpm": rpm_name,
			}

			ok, self.packages[rpm_name] = self.ff.bake("etcdstoragereader").call(data)
			if not ok:
				missing_rpms.append(rpm)
				continue

			data["artefact"] = ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API
			ok, self.exported_api[rpm_name] = self.ff.bake("etcdstoragereader").call(data)
			if not ok:
				missing_rpms.append(rpm)
				continue

		if missing_rpms == []:
			return True

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

		# extract api for each missing rpm
		for rpm in missing_rpms:
			# generate resource specification for rpm
			resource = ResourceSpecifier().generateRpm(
				self.product,
				self.distribution,
				self.build,
				rpm["name"]
			)
			data = {
				"product": self.product,
				"directories_to_skip": rpm["skipped_directories"] if "skipped_directories" in rpm else [],
				"distribution": self.distribution,
				"build": self.build,
				"rpm": rpm["name"],
				"resource": resource,
				"project": project,
				"commit": commit,
				"ipprefix": ipprefix
			}

			data = self.ff.bake("distributiongosymbolsextractor").call(data)
			self.packages[rpm["name"]] = self._getArtefactFromData(ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES, data)
			self.exported_api[rpm["name"]] = self._getArtefactFromData(ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API, data)

			# TODO(jchaloup): only for testing purposes atm, make an option for storing
			for artefact in data:
				data = self.ff.bake("etcdstoragewriter").call(artefact)

		return True
