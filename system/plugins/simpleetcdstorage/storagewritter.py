import logging
import json
from system.core.meta.metastoragewritter import MetaStorageWritter
from artefactdriverfactory import ArtefactDriverFactory

class StorageWritter(MetaStorageWritter):

	def store(self, data):
		"""Store artefact into storage

		param data: artefact writtable to storage
		type  data: dictionary
		"""
		if "artefact" not in data:
			logging.error("artefact key not found in %s" % json.dumps(data))
			return False
	
		driver = ArtefactDriverFactory().build(data["artefact"])
		if driver == None:
			logging.error("artefact driver for %s not found" % data["artefact"])
			return False

		if not driver.store(data):
			return False

		return True

