from infra.system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangProjectDistributionPackagesKeyGenerator(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "product", "distribution", "build", "rpm"]:
			if key not in data:
				raise ValueError("golang-project-distribution-packages: %s key missing" % key)

			keys.append(self.truncateKey(data[key]))

		return delimiter.join(keys)
