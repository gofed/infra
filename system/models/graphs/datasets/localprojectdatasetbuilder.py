from .datasetbuilder import DatasetBuilder
from infra.system.core.factory.actfactory import ActFactory
from .types import DatasetError
from infra.system.core.functions.types import FunctionFailedError

class LocalProjectDatasetBuilder(object):

	def __init__(self, directory, ipprefix):
		self.directory = directory
		self.ipprefix = ipprefix
		self.act = ActFactory().bake("go-code-inspection")

	def build(self):
		data = {
			"type": "user_directory",
			"ipprefix": self.ipprefix,
			"resource": self.directory
		}

		builder = DatasetBuilder()

		try:
			artefact = self.act.call(data)
		except FunctionFailedError as e:
			raise DatasetError("Unable to create dataset: %s" % e)

		builder.addArtefact(artefact)

		return builder.build().dataset()
