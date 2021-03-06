from infra.system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangProjectApiDiffKeyGenerator(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "repository", "commit1", "commit2"]:
			if key not in data:
				raise ValueError("golang-project-api-diff: %s key missing" % key)

			keys = keys + self.value2key(data[key], delimiter, key, {"repository": ["provider", "username", "project"]})

		return keys
