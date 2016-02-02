from system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangProjectToPackageNameKeyGenerator(MetaArtefactKeyGenerator):
	"""
	Artefact in question:
	{
	"artefact": "golang-project-to-package-name",
	"product": "Fedora|RHEL",
	"distribution": "f21|f22|rhel-7.2|centos-7",
	"project": "github.com/coreos/etcd",
	"name": "etcd|coreos-etcd|..."
	}
	"""

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "product", "distribution", "project"]:
			if key not in data:
				logging.error("golang-project-to-package-name: %s key missing" % key)
				return ""

			keys.append(data[key])

		return delimiter.join(keys)


