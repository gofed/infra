from system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangProjectPackagesKeyGenerator(MetaArtefactKeyGenerator):
	"""
	Artefact in question:
	{
	"artefact": "golang-project-info-fedora",
	"project", "github.com/coreos/etcd",
	"commit", "729b530c489a73532843e664ae9c6db5c686d314",
	...
	}
	"""

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "project", "commit"]:
			if key not in data:
				logging.error("golang-project-packages: %s key missing" % key)
				return ""

			keys.append(data[key])

		return delimiter.join(keys)


