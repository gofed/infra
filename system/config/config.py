import ConfigParser

class Config(object):

	def __init__(self):
		self.config_file = "/home/jchaloup/Projects/gofed/infra/system/config/infra.conf"
		self._parse(self.config_file)


	def _parse(self, config_file):
		self.config = ConfigParser.ConfigParser()
		self.config.read(config_file)

	def readStoragePlugin(self):
		return self.config.get("storage", "readplugin")

	def writeStoragePlugin(self):
		return self.config.get("storage", "writeplugin")

	def storeArtefacts(self):
		return self.config.get("storage", "write") == "true"

	def retrieveArtefacts(self):
		return self.config.get("storage", "read") == "true"

