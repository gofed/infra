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

		return ArtefactDriverFactory().build(data["artefact"]).store(data)

