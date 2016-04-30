import ConfigParser
import os
from gofed_lib.utils import getScriptDir

class Config(object):

	def __init__(self):
		if "GOFED_DEVEL" in os.environ:
			self.config_file = "%s/infra.conf" % getScriptDir(__file__)
		else:
			self.config_file = "/etc/gofed/infra.conf"

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

