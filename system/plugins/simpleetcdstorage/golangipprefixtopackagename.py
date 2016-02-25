from .artefactdriver import ArtefactDriver
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME

class GolangIpprefixToPackageNameDriver(ArtefactDriver):

	def __init__(self):

		ArtefactDriver.__init__(self, ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME)
