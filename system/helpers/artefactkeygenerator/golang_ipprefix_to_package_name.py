from metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangIPPrefixToPackageNameKeyGenerator(MetaArtefactKeyGenerator):
	"""
	Artefact in question:
	{
	"artefact": "golang-project-to-package-name",
	"product": "Fedora|RHEL",
	"distribution": "f21|f22|rhel-7.2|centos-7",
	"ipprefix": "github.com/coreos/etcd",
	"name": "etcd"
	}
	"""

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "product", "distribution", "ipprefix"]:
			if key not in data:
				logging.error("golang-ipprefix-to-package-name: %s key missing" % key)
				return ""

			keys.append(data[key])

		return delimiter.join(keys)


