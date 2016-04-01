from infra.system.core.meta.metaact import MetaAct
from infra.system.resources.specifier import ResourceSpecifier
from infra.system.resources import types
from infra.system.helpers.utils import getScriptDir
from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_IPPREFIX_TO_RPM
)

class ArtefactReaderAct(MetaAct):

	def __init__(self):
		MetaAct.__init__(
			self,
			"%s/input_schema.json" % getScriptDir(__file__)
		)

		# TODO(jchaloup): extend the input schema to support query for multiple artefacts
		self.artefact = {}

	def setData(self, data):
		"""Validation and data pre-processing"""
		if not self._validateInput(data):
			return False

		# at this point it is enough to forward the data to storage reader
		self.data = data

		# supporting only mapping atm
		# TODO(jchaloup): extend the artefact to the rest once documented
		if data["artefact"] == ARTEFACT_GOLANG_IPPREFIX_TO_RPM:
			return True

		return False

	def getData(self):
		"""Validation and data post-processing"""
		return self.artefact

	def execute(self):
		"""Impementation of concrete data processor"""
		ok, self.artefact = self.ff.bake("etcdstoragereader").call(self.data)
		if ok:
			return True

		return False
