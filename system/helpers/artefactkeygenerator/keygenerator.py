from system.artefacts import artefacts
from golang_ipprefix_to_package_name import GolangIPPrefixToPackageNameKeyGenerator
from golang_project_info_fedora import GolangProjectInfoFedoraKeyGenerator
from golang_project_to_package_name import GolangProjectToPackageNameKeyGenerator
from golang_project_exported_api import GolangProjectExportedAPIKeyGenerator
from golang_projects_api_diff import GolangProjectsAPIDiffKeyGenerator
from golang_project_packages import GolangProjectPackagesKeyGenerator

class KeyGeneratorFactory:

	def build(self, artefact):
		if artefact == artefacts.ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME:
			return GolangIPPrefixToPackageNameKeyGenerator()

		#if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_PACKAGES
		#	return 

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_EXPORTED_API:
			return GolangProjectExportedAPIKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_INFO_FEDORA:
			return GolangProjectInfoFedoraKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME:
			return GolangProjectToPackageNameKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECTS_API_DIFF:
			return GolangProjectsAPIDiffKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_PACKAGES:
			return GolangProjectPackagesKeyGenerator()

		return None
