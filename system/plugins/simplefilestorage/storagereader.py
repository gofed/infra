import logging
import json
from infra.system.core.meta.metastoragereader import MetaStorageReader
from .artefactdriverfactory import ArtefactDriverFactory

class StorageReader(MetaStorageReader):

	def retrieve(self, data):
		"""Retrieve artefact from storage

		param data: artefact key to retrieve
		type  data: dictionary
		"""
		if "artefact" not in data:
			raise ValueError("artefact key not found in %s" % json.dumps(data))

		driver = ArtefactDriverFactory().build(data["artefact"])
		if driver == None:
			raise KeyError("artefact driver for %s not found" % data["artefact"])

		return driver.retrieve(data)
