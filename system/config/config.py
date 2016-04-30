from gofed_lib.config.config import Config
from gofed_lib.utils import getScriptDir

class InfraConfig(Config):

	def __init__(self):
		Config.__init__(self, "infra.conf")

	def _classDir(self):
		return getScriptDir(__file__)

	def readStoragePlugin(self):
		return self._config.get("storage", "readplugin")

	def writeStoragePlugin(self):
		return self._config.get("storage", "writeplugin")

	def storeArtefacts(self):
		return self._config.get("storage", "write") == "true"

	def retrieveArtefacts(self):
		return self._config.get("storage", "read") == "true"

	def resourceClientDirectory(self):
		return self._config.get("resources", "client_dir")

	def simpleFileStorageWorkingDirectory(self):
		return self._config.get("simplefilestorage", "working_directory")
