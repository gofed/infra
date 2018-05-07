from infra.system.artefacts import artefacts
from .golangprojectdistributionexportedapi import GolangProjectDistributionExportedApiKeyGenerator
from .golangprojectdistributionpackages import GolangProjectDistributionPackagesKeyGenerator
from .golangipprefixtopackagename import GolangIpprefixToPackageNameKeyGenerator
from .golangprojectexportedapi import GolangProjectExportedApiKeyGenerator
from .golangprojectpackages import GolangProjectPackagesKeyGenerator
from .golangprojectinfofedora import GolangProjectInfoFedoraKeyGenerator
from .golangprojectapidiff import GolangProjectApiDiffKeyGenerator
from .golangprojecttopackagename import GolangProjectToPackageNameKeyGenerator
from .golangprojectcontentmetadata import GolangProjectContentMetadataKeyGenerator
from .golangprojectrepositoryinfo import GolangProjectRepositoryInfoKeyGenerator
from .golangprojectrepositorycommit import GolangProjectRepositoryCommitKeyGenerator
from .golangprojectdistributionpackagebuilds import GolangProjectDistributionPackageBuildsKeyGenerator
from .golangprojectdistributionbuild import GolangProjectDistributionBuildKeyGenerator
from .cachegolangprojectrepositorycommits import CacheGolangProjectRepositoryCommitsKeyGenerator
from .golangipprefixtorpm import GolangIpprefixToRpmKeyGenerator
from .golangdistributionsnapshot import GolangDistributionSnapshotKeyGenerator
from .cachegolangprojectdistributionpackagebuilds import CacheGolangProjectDistributionPackageBuildsKeyGenerator
from .golangprojectapi import GolangProjectApiKeyGenerator
from .golangprojectcontracts import GolangProjectContractsKeyGenerator
from .golangprojectstaticallocations import GolangProjectStaticAllocationsKeyGenerator

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

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA:
			return GolangProjectContentMetadataKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO:
			return GolangProjectRepositoryInfoKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT:
			return GolangProjectRepositoryCommitKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS:
			return GolangProjectDistributionPackageBuildsKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD:
			return GolangProjectDistributionBuildKeyGenerator()

		if artefact == artefacts.ARTEFACT_CACHE_GOLANG_PROJECT_REPOSITORY_COMMITS:
			return CacheGolangProjectRepositoryCommitsKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_IPPREFIX_TO_RPM:
			return GolangIpprefixToRpmKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT:
			return GolangDistributionSnapshotKeyGenerator()

		if artefact == artefacts.ARTEFACT_CACHE_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS:
			return CacheGolangProjectDistributionPackageBuildsKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_API:
			return GolangProjectApiKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_CONTRACTS:
			return GolangProjectContractsKeyGenerator()

		if artefact == artefacts.ARTEFACT_GOLANG_PROJECT_STATIC_ALLOCATIONS:
			return GolangProjectStaticAllocationsKeyGenerator()

		raise ValueError("Invalid artefact: %s" % artefact)