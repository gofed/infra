from .datasetbuilder import DatasetBuilder
from infra.system.core.factory.actfactory import ActFactory
from .types import DatasetError
from infra.system.core.functions.types import FunctionFailedError
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES

class ProjectDatasetBuilder(object):

	def __init__(self, repository, commit, ipprefix):
		self.repository = repository
		self.commit = commit
		self.ipprefix = ipprefix
		self.act = ActFactory().bake("go-code-inspection")

	def build(self):
		data = {
			"type": "upstream_source_code",
			"repository": self.repository,
			"commit": self.commit,
			"ipprefix": self.ipprefix
		}

		builder = DatasetBuilder()

		try:
			artefact = self.act.call(data)
		except FunctionFailedError as e:
			raise DatasetError("Unable to create dataset: %s" % e)

		builder.addArtefact(artefact[ARTEFACT_GOLANG_PROJECT_PACKAGES])

		return builder.build().dataset()
