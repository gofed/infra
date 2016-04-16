from infra.system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangProjectDistributionPackageBuildsKeyGenerator(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "product", "distribution", "package"]:
			if key not in data:
				raise ValueError("golang-project-distribution-package-builds: %s key missing" % key)

			keys.append(self.truncateKey(data[key]))

		return keys
