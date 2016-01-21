class MetaArtefactDriver:
	"""
	The class declares methods for storing/retriving artefact
	or a list of artefacts.
	Implementation of all artefact drivers must inherit from this class
	and implement all methods.
	"""

	def store(self, data):
		"""store artefact"""
		raise NotImplementedError

	def retrieve(self, key):
		"""retrieve artefact"""
		raise NotImplementedError

	def storeList(self, dataList):
		"""store list of artefacts"""
		raise NotImplementedError

	def retrieveList(self, key):
		"""retrieve list of artefacts"""
		raise NotImplementedError

