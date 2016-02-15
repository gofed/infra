
from system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangIpprefixToPackageNameKeyGenerator(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "product", "distribution", "ipprefix"]:
			if key not in data:
				logging.error("golang-ipprefix-to-package-name: %s key missing" % key)
				return ""

			keys.append(data[key])

		return delimiter.join(keys)
