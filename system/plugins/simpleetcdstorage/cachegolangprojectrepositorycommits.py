from .artefactdriver import ArtefactDriver
from infra.system.artefacts.artefacts import ARTEFACT_CACHE_GOLANG_PROJECT_REPOSITORY_COMMITS

class CacheGolangProjectRepositoryCommitsDriver(ArtefactDriver):

	def __init__(self):

		ArtefactDriver.__init__(self, ARTEFACT_CACHE_GOLANG_PROJECT_REPOSITORY_COMMITS)
