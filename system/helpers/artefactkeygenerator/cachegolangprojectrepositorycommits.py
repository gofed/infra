from infra.system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class CacheGolangProjectRepositoryCommitsKeyGenerator(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "repository"]:
			if key not in data:
				raise ValueError("cache-golang-project-repository-commits: %s key missing" % key)

			keys.append(self.value2key(data[key], delimiter, key, {"repository": ["provider", "username", "project"]}))

		return delimiter.join(keys)
