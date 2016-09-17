from infra.system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangProjectInfoFedoraKeyGenerator(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "project", "distribution"]:
			if key not in data:
				raise ValueError("golang-project-info-fedora: %s key missing" % key)

			keys.append(self.truncateKey(data[key]))

		return keys
