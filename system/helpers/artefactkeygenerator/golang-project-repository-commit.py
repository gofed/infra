from system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
from system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT
import logging

class GolangProjectRepositoryCommitKeyGenerator(MetaArtefactKeyGenerator):
	"""
	{
	"artefact": golang-project-repository-commit,
	"repository": "github.com/coreos/etcd",
	"commit": "729b530c489a73532843e664ae9c6db5c686d314"
	"adate": timestamp,
	"cdate": timestamp,
	"author": "Gyu-Ho Lee <gyuhox@gmail.com>",
	"message": "commit message ..."
	}
	"""
	def generate(self, data, delimiter=":"):
		# return a list of fields
		keys = []
		for key in ["artefact","repository", "commit","adate", "cdate", "author", "message"]:
			if key not in data:
				logging.error("%s: %s key missing" % (ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT, key))
				return ""

			keys.append(data[key])

		return delimiter.join(keys)
