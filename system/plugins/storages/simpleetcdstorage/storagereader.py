import logging
import json
from system.plugins.storages.metastoragereader import MetaStorageReader
from artefactdriverfactory import ArtefactDriverFactory

class StorageReader(MetaStorageReader):

	def retrieve(self, data):
		"""Retrieve artefact from storage

		param data: artefact key to retrieve
		type  data: dictionary
		"""
		if "artefact" not in data:
			logging.error("artefact key not found in %s" % json.dumps(data))
			return False, {}

		driver = ArtefactDriverFactory().build(data["artefact"])
		if driver == None:
			logging.error("artefact driver for %s not found" % data["artefact"])
			return False, {}

		return driver.retrieve(data)
