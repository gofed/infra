from infra.system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangProjectContractsKeyGenerator(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "ipprefix", "hexsha"]:
			if key not in data:
				raise ValueError("golang-project-contracts: %s key missing" % key)

			keys.append(self.truncateKey(data[key]))

		return keys
