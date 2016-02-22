from infra.system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangProjectRepositoryInfoKeyGenerator(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "project"]:
			if key not in data:
				logging.error("golang-project-repository-info: %s key missing" % key)
				return ""

			keys.append(data[key])

		return delimiter.join(keys)
