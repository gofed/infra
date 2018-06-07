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
			"ipprefix": self.ipprefix,
			"hexsha": self.commit,
		}

		try:
			packages_artefact = StorageReader().retrieve(artefact_key)
		except KeyError:
			Worker("go/codeanalysis/golistextractor").setPayload({
				"project": self.repository,
				"hexsha": self.commit,
				"ipprefix": self.ipprefix,
			}).do()
			packages_artefact = StorageReader().retrieve(artefact_key)

		builder = DatasetBuilder()
		builder.addArtefact(packages_artefact)
		return builder.build().dataset()
