from infra.system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangDistributionSnapshotKeyGenerator(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "distribution"]:
			if key not in data:
				raise ValueError("golang-distribution-snapshot: %s key missing" % key)

			keys = keys + self.value2key(data[key], delimiter, key, {"distribution": ["product", "version"]})

		return keys
