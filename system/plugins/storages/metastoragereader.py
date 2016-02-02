class MetaStorageReader:

	def retrieve(self, data):
		"""Retrieve artefact from storage

		param data: artefact key to retrieve
		type  data: dictionary
		"""
		raise NotImplementedError

	def retrieveList(self, data):
		"""Retrieve artefacts from storage. Returns True|False, [artefact].
		If any artefact is not retrieved, False and remaining list of artefacts is returned.

		param data: list of artefact keys to retrieve from storage
		type  data: [dictionary]
		"""
		success = True
		artefacts = []
		for item in data:
			r, a = self.retrieve(item)
			if not r:
				success = False
			else:
				artefacts.append(a)

		return success, artefacts
