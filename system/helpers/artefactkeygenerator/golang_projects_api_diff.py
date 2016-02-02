from system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
from system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECTS_API_DIFF
import logging

class GolangProjectsAPIDiffKeyGenerator(MetaArtefactKeyGenerator):
	"""
	Artefact in question:
	{
	"artefact": "golang-project-exported-api",
	"project", "github.com/coreos/etcd",
	"commit1", "729b530c489a73532843e664ae9c6db5c686d314",
	"commit2", "729b530c489a73532843e664ae9c6db5c686d314",
	...
	}
	"""

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "project", "commit1", "commit2"]:
			if key not in data:
				logging.error("%s: %s key missing" % (ARTEFACT_GOLANG_PROJECTS_API_DIFF, key))
				return ""

			keys.append(data[key])

		return delimiter.join(keys)


