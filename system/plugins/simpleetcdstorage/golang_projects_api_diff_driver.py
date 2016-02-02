from artefactdriver import ArtefactDriver
from system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECTS_API_DIFF

class GolangProjectsAPIDiffDriver(ArtefactDriver):

	def __init__(self):
		ArtefactDriver.__init__(self,  ARTEFACT_GOLANG_PROJECTS_API_DIFF)
