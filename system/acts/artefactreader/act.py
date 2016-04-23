from infra.system.core.meta.metaact import MetaAct
from infra.system.resources import types
from gofed_lib.utils import getScriptDir
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_IPPREFIX_TO_RPM,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES,
	ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT,
	ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS
)

class ArtefactReaderAct(MetaAct):

	def __init__(self):
		MetaAct.__init__(
			self,
			"%s/input_schema.json" % getScriptDir(__file__)
		)

		# TODO(jchaloup): extend the input schema to support query for multiple artefacts
		self._artefact = {}

	def setData(self, data):
		"""Validation and data pre-processing"""
		if not self._validateInput(data):
			return False

		# at this point it is enough to forward the data to storage reader
		self.data = data

		# supporting only mapping atm
		# TODO(jchaloup): extend the artefact to the rest once documented
		if data["artefact"] in [
			ARTEFACT_GOLANG_IPPREFIX_TO_RPM,
			ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES,
			ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT,
			ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS
			]:
			return True

		# TODO(jchaloup): raise exception when artefact not supported
		return False

	def getData(self):
		"""Validation and data post-processing"""
		return self._artefact

	def execute(self):
		"""Impementation of concrete data processor"""
		if not self.retrieve_artefacts:
			return False

		# TODO(jchaloup): raise exception when artefact not found
		try:
			self._artefact = self.ff.bake(self.read_storage_plugin).call(self.data)
		except KeyError:
			return False

		return True
