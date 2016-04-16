import logging
import json
from infra.system.core.meta.metastoragewriter import MetaStorageWriter
from .artefactdriverfactory import ArtefactDriverFactory

class StorageWriter(MetaStorageWriter):

	def store(self, data):
		"""Store artefact into storage

		param data: artefact writable to storage
		type  data: dictionary
		"""
		if "artefact" not in data:
			raise KeyError("artefact key not found in %s" % json.dumps(data))
	
		driver = ArtefactDriverFactory().build(data["artefact"])
		if driver == None:
			raise KeyError("artefact driver for %s not found" % data["artefact"])

		if not driver.store(data):
			return False

		return True

