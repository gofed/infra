from .artefactdriver import ArtefactDriver
from infra.system.artefacts.artefacts import ARTEFACT_CACHE_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS

class CacheGolangProjectDistributionPackageBuildsDriver(ArtefactDriver):

	def __init__(self):

		ArtefactDriver.__init__(self, ARTEFACT_CACHE_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS)
