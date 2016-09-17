class MetaStorageWriter:

	def store(self, data):
		"""Store artefact into storage

		param data: artefact writtable to storage
		type  data: dictionary
		"""
		raise NotImplementedError

	def storeList(self, data):
		"""Store artefacts into storage. If any artefact is not stored, return False.

		param data: list of artefacts writtable to storage
		type  data: [dictionary]
		"""
		success = True
		for item in data:
			if not self.store(item):
				success = False

		return success
