from artefactdriver import ArtefactDriver
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECTS_API_DIFF

class GolangProjectApiDiffDriver(ArtefactDriver):

	def __init__(self):

		ArtefactDriver.__init__(self, ARTEFACT_GOLANG_PROJECTS_API_DIFF)
