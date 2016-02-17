from infra.system.artefacts import artefacts
from golangprojectdistributionexportedapi import GolangProjectDistributionExportedApiKeyGenerator
from golangprojectdistributionpackages import GolangProjectDistributionPackagesKeyGenerator
from golangipprefixtopackagename import GolangIpprefixToPackageNameKeyGenerator
from golangprojectexportedapi import GolangProjectExportedApiKeyGenerator
from golangprojectpackages import GolangProjectPackagesKeyGenerator
from golangprojectinfofedora import GolangProjectInfoFedoraKeyGenerator
from golangprojectapidiff import GolangProjectApiDiffKeyGenerator
from golangprojecttopackagename import GolangProjectToPackageNameKeyGenerator

class KeyGeneratorFactory:

	def build(self, artefact):

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API:
			return GolangProjectDistributionExportedApiKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES:
			return GolangProjectDistributionPackagesKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME:
			return GolangIpprefixToPackageNameKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_EXPORTED_API:
			return GolangProjectExportedApiKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_PACKAGES:
			return GolangProjectPackagesKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_INFO_FEDORA:
			return GolangProjectInfoFedoraKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECTS_API_DIFF:
			return GolangProjectApiDiffKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME:
			return GolangProjectToPackageNameKeyGenerator()

		raise ValueError("Invalid artefact: %s" % artefact)