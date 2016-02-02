from system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangProjectInfoFedoraKeyGenerator(MetaArtefactKeyGenerator):
	"""
	Artefact in question:
	{
	"artefact": "golang-project-info-fedora",
	"distribution": "f23",
	"project", "github.com/coreos/etcd",
	"commit", "729b530c489a73532843e664ae9c6db5c686d314",
	"last-updated": "2015-12-12"
	}
	"""

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "project", "distribution"]:
			if key not in data:
				logging.error("golang-project-info-fedora: %s key missing" % key)
				return ""

			keys.append(data[key])

		return delimiter.join(keys)


