from .datasetbuilder import DatasetBuilder
from system.core.factory.actfactory import ActFactory
from .types import DatasetError
from infra.system.core.functions.types import FunctionFailedError

class ProjectDatasetBuilder(object):

	def __init__(self, project, commit):
		self.project = project
		self.commit = commit
		self.act = ActFactory().bake("go-code-inspection")

	def build(self):
		data = {
			"type": "upstream_source_code",
			"project": self.project,
			"commit": self.commit,
			"ipprefix": self.project,
			"directories_to_skip": []
		}

		builder = DatasetBuilder()

		try:
			artefact = self.act.call(data)
		except FunctionFailedError as e:
			raise DatasetError("Unable to create dataset: %s" % e)

		builder.addArtefact(artefact)

		return builder.build().dataset()
