from .datasetbuilder import DatasetBuilder
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES
from gofedlib.providers.providerbuilder import ProviderBuilder
from infra.system.plugins.simplefilestorage.storagereader import StorageReader
from infra.system.workers import Worker

class ProjectDatasetBuilder(object):

	def __init__(self, repository, commit, ipprefix):
		self.repository = repository
		self.commit = commit
		self.ipprefix = ipprefix

	def build(self):
		artefact_key = {
			"artefact": ARTEFACT_GOLANG_PROJECT_PACKAGES,
			"repository": ProviderBuilder().buildUpstreamWithLocalMapping().parse(self.repository).signature(),
			"commit": self.commit,
		}

		try:
			packages_artefact = StorageReader().retrieve(artefact_key)
		except KeyError:
			Worker("gocodeinspection").setPayload({
				"repository": self.repository,
				"commit": self.commit,
				"ipprefix": self.ipprefix,
			}).do()
			packages_artefact = StorageReader().retrieve(artefact_key)

		builder = DatasetBuilder()
		builder.addArtefact(packages_artefact)
		return builder.build().dataset()
