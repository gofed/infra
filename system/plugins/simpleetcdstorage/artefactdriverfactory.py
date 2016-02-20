from infra.system.artefacts import artefacts
from golangprojectdistributionexportedapi import GolangProjectDistributionExportedApiDriver
from golangprojectdistributionpackages import GolangProjectDistributionPackagesDriver
from golangipprefixtopackagename import GolangIpprefixToPackageNameDriver
from golangprojectexportedapi import GolangProjectExportedApiDriver
from golangprojectpackages import GolangProjectPackagesDriver
from golangprojectinfofedora import GolangProjectInfoFedoraDriver
from golangprojectapidiff import GolangProjectApiDiffDriver
from golangprojecttopackagename import GolangProjectToPackageNameDriver
from golangprojectcontentmetadata import GolangProjectContentMetadataDriver

class ArtefactDriverFactory:

	def build(self, artefact):

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API:
			return GolangProjectDistributionExportedApiDriver()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES:
			return GolangProjectDistributionPackagesDriver()

		if artefact == artefacts.ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME:
			return GolangIpprefixToPackageNameDriver()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_EXPORTED_API:
			return GolangProjectExportedApiDriver()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_PACKAGES:
			return GolangProjectPackagesDriver()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_INFO_FEDORA:
			return GolangProjectInfoFedoraDriver()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECTS_API_DIFF:
			return GolangProjectApiDiffDriver()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME:
			return GolangProjectToPackageNameDriver()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA:
			return GolangProjectContentMetadataDriver()

		raise ValueError("Invalid artefact: %s" % artefact)