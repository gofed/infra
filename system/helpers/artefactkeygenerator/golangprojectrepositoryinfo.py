from infra.system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangProjectRepositoryInfoKeyGenerator(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "repository"]:
			if key not in data:
				raise ValueError("golang-project-repository-info: %s key missing" % key)

			keys = keys + self.value2key(data[key], delimiter, key, {"repository": ["provider", "username", "project"]})

		return keys
