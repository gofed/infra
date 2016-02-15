from system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangProjectDistributionPackagesKeyGenerator(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "product", "distribution", "build", "rpm"]:
			if key not in data:
				logging.error("golang-project-distribution-packages: %s key missing" % key)
				return ""

			keys.append(data[key])

		return delimiter.join(keys)
