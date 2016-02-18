from system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
from system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO
import logging


class GolangProjectRepositoryInfo(MetaArtefactKeyGenerator):
	"""
	{
	"artefact: "golang-project-repository-info",
	"project": "github.com/coreos/etcd",
	"repository": "github.com/coreos/etcd",
	"clone_url": "github.com/coreos/etcd.git",
	"branches": ["master", "release-0.4", "release-2.0", "..."],
	"commits": ["cb7ebe81a88e21ca3860f4b830cc2ee7304f6b2f",
		"1b7b20f4f82c39c2cb21f79d4d1d30edf0b7ceeb", "..."]
	}
	"""

	def generate(self, data, delimiter=":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "project", "repository", "clone_url", "branches", "commits"]:
			if key not in data:
				logging.error("%s: %s key missing" % (ARTEFACT_GOLANG_PROJECT_REPOSITORY_INFO, key))
				return ""

			keys.append(data[key])

		return delimiter.join(keys)
