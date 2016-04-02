from infra.system.core.meta.metaact import MetaAct
from infra.system.resources.specifier import ResourceSpecifier
from infra.system.resources import types
from infra.system.helpers.utils import getScriptDir
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECT_INFO_FEDORA,
	ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API,
	ARTEFACT_GOLANG_IPPREFIX_TO_RPM
)
from gofed_lib.helpers import Build, Rpm

class ScanDistributionBuildAct(MetaAct):

	def __init__(self):
		MetaAct.__init__(
			self,
			"%s/input_schema.json" % getScriptDir(__file__)
		)

		self.exported_api = {}
		self.packages = {}
		self.mappings = {}

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
			"packages": self.packages,
			"mappings": self.mappings
		}

	def _getIpprefix2RpmArtefact(self, build, product, info_artefact, packages_artefacts):
		"""For each rpm in packages, construct the mapping

		"""
		artefacts = []
		for rpm in packages_artefacts:
			# Filter out all non-devel rpms
			name = Rpm(build, rpm).name()
			if name.endswith("unit-test-devel") or name.endswith("unit-test"):
				continue

			for prefix in packages_artefacts[rpm]["data"]:
				 artefacts.append({
					"artefact": ARTEFACT_GOLANG_IPPREFIX_TO_RPM,
					"ipprefix": prefix["ipprefix"],
					"commit": info_artefact["commit"],
					"rpm": rpm,
					"product": product,
					"distribution": info_artefact["distribution"],
					"build": build
				})

		return artefacts

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

		info_artefact = {}
		for artefact in data:
			if artefact["artefact"] == ARTEFACT_GOLANG_PROJECT_INFO_FEDORA:
				info_artefact = artefact
				break

		# TODO(jchaloup): each ipprefix can have its own commit
		commit = info_artefact["commit"]

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
				"commit": commit
			}

			data = self.ff.bake("distributiongosymbolsextractor").call(data)
			self.packages[rpm["name"]] = self._getArtefactFromData(ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES, data)
			self.exported_api[rpm["name"]] = self._getArtefactFromData(ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API, data)

			# TODO(jchaloup): only for testing purposes atm, make an option for storing
			for artefact in data:
				rdata = self.ff.bake("etcdstoragewriter").call(artefact)

		mapping_artefacts = self._getIpprefix2RpmArtefact(self.build, self.product, info_artefact, self.packages)

		for artefact in mapping_artefacts:
			self.mappings[artefact["ipprefix"]] = artefact

		# TODO(jchaloup): only for testing purposes atm, make an option for storing
		# Everytime there is at least one rpm missing (or srpm), new mapping artefacts can get (re)generated
		for artefact in mapping_artefacts:
			rdata = self.ff.bake("etcdstoragewriter").call(artefact)

		return True
