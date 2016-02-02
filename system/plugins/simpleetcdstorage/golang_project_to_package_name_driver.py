from artefactdriver import ArtefactDriver
from system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME

class GolangProjectToPackageNameDriver(ArtefactDriver):

	def __init__(self):
		ArtefactDriver.__init__(self,  ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME)
