from infra.system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class GolangProjectInfoFedoraKeyGenerator(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = ":"):
		# return a list of fields
		keys = []
		for key in ["artefact", "project", "distribution"]:
			if key not in data:
				logging.error("golang-project-info-fedora: %s key missing" % key)
				return ""

			keys.append(data[key])

		return delimiter.join(keys)
