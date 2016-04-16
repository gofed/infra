from infra.system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangProjectContentMetadataKeyGenerator(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "project", "commit"]:
			if key not in data:
				raise ValueError("golang-project-content-metadata: %s key missing" % key)

			keys.append(self.truncateKey(data[key]))

		return keys
