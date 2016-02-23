from infra.system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangProjectRepositoryCommitKeyGenerator(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "repository", "commit"]:
			if key not in data:
				logging.error("golang-project-repository-commit: %s key missing" % key)
				return ""

			keys.append(data[key])

		return delimiter.join(keys)
