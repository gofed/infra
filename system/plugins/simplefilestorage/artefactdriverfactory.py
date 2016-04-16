from infra.system.artefacts import artefacts
from .artefactdriver import ArtefactDriver

class ArtefactDriverFactory(object):

	def __init__(self):
		self.working_directory = "/var/lib/gofed/simplefilestorage"
		self.artefacts = []

		self.artefacts.append(artefacts.ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_EXPORTED_API)
		self.artefacts.append(artefacts.ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGES)
		self.artefacts.append(artefacts.ARTEFACT_GOLANG_IPPREFIX_TO_PACKAGE_NAME)
		self.artefacts.append(artefacts.ARTEFACT_GOLANG_PROJECT_EXPORTED_API)
		self.artefacts.append(artefacts.ARTEFACT_GOLANG_PROJECT_PACKAGES)
		self.artefacts.append(artefacts.ARTEFACT_GOLANG_PROJECT_INFO_FEDORA)
		self.artefacts.append(artefacts.ARTEFACT_GOLANG_PROJECTS_API_DIFF)
		self.artefacts.append(artefacts.ARTEFACT_GOLANG_PROJECT_TO_PACKAGE_NAME)
		self.artefacts.append(artefacts.ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA)
		self.artefacts.append(artefacts.ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO)
		self.artefacts.append(artefacts.ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT)
		self.artefacts.append(artefacts.ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS)
		self.artefacts.append(artefacts.ARTEFACT_GOLANG_PROJECT_DISTRIBUTION_BUILD)
		self.artefacts.append(artefacts.ARTEFACT_CACHE_GOLANG_PROJECT_REPOSITORY_COMMITS)
		self.artefacts.append(artefacts.ARTEFACT_GOLANG_IPPREFIX_TO_RPM)
		self.artefacts.append(artefacts.ARTEFACT_GOLANG_DISTRIBUTION_SNAPSHOT)
		self.artefacts.append(artefacts.ARTEFACT_CACHE_GOLANG_PROJECT_DISTRIBUTION_PACKAGE_BUILDS)

	def build(self, artefact):
		if artefact not in self.artefacts:
			raise KeyError("Artefact '%s' not supported" % artefact)

		return ArtefactDriver(self.working_directory, artefact)