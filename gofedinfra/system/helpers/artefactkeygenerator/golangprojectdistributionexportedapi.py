from infra.system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangProjectDistributionExportedApiKeyGenerator(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "product", "distribution", "build", "rpm"]:
			if key not in data:
				raise ValueError("golang-project-distribution-exported-api: %s key missing" % key)

			keys.append(self.truncateKey(data[key]))

		return keys
