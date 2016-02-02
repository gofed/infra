from system.artefacts import artefacts
from golang_ipprefix_to_package_name_driver import GolangIPPrefixToPackageNameDriver
from golang_project_exported_api_driver import GolangProjectExportedAPIDriver
from golang_project_info_fedora_driver import GolangProjectInfoFedoraDriver
from golang_projects_api_diff_driver import GolangProjectsAPIDiffDriver
from golang_project_to_package_name_driver import GolangProjectToPackageNameDriver

class ArtefactDriverFactory:

	def build(self, artefact):

		if artefact == artefacts.ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME:
			return GolangIPPrefixToPackageNameDriver()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_EXPORTED_API:
			return GolangProjectExportedAPIDriver()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_INFO_FEDORA:
			return GolangProjectInfoFedoraDriver()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME:
			return GolangProjectToPackageNameDriver()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECTS_API_DIFF:
			return GolangProjectsAPIDiffDriver()

		return None
