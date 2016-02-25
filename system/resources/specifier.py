from .types import *

class ResourceSpecifier:
	"""
	Generates resource specifier for given resource.
	It does not specify where or how to retrieve a resource.
	It only specifies what resource is request
	and what is expecting form of its subresource.
	"""
	def generateRpm(self, product, distribution, build, rpm, subresource = SUBRESOURCE_DIRECTORY_TREE):
		"""Generate resource specifier for distribution rpm.

		:param product: OS Product (e.g. Fedora, CentOS, etc.).
		:type  product: str
		:param distribution: distribution of OS (e.g. F22, centos7, etc.).
		:type  distribution: str
		:param build: build which contain required rpm.
		:type  build: str
		:param rpm: rpm which contain required subresource.
		:type  rpm: str
		:param subresource: demanded subresource (e.g. directory tree, spec file, etc.)
		:type  subresource: str
		"""
		return {
			"product": product,	# Fedora => Koji, CentOs => CentOS Koji, etc.
			"distribution": distribution,
			"build": build,
			"rpm": rpm,
			"resource": RESOURCE_RPM,
			"resource-type": RESOURCE_TYPE_RPM,
			"subresource": subresource
		}

	def generateUserDirectory(self, location, type = RESOURCE_TYPE_TARBALL, subresource = SUBRESOURCE_DIRECTORY_TREE):
		"""Generate resource specifier for user directory.

		:param location: location of directory (e.g local path, ftp, http, etc.).
		:type  location: str
		:param subresource: demanded subresource (e.g. directory tree, spec file, etc.).
		:type  subresource: str
		:param type: resource type, how is a given resource stored (e.g. tarball, directory, file, etc.)
		:type  type: str
		"""
		if not location.startswith("file://"):
			location = "file://%s" % location

		return {
			"resource": RESOURCE_USER_DIRECTORY,
			"subresource": subresource,
			"resource-type": type,
			"location": location
		}

	def generateUpstreamSourceCode(self, project, commit, subresource = SUBRESOURCE_DIRECTORY_TREE):
		"""Generate resource specifier for source codes for given upstream project

		:param project: unique project name
		:type  project: str
		:param commit: commit of a project to take source codes from
		:type  commit: str
		:param subresource: demanded subresource (e.g. directory tree, spec file, etc.).
		:type  subresource: str	
		"""
		return {
			"project": project,
			"commit": commit,
			"resource": RESOURCE_UPSTREAM_SOURCE_CODES,
			"subresource": subresource
		}

