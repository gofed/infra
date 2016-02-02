class MetaArtefactKeyGenerator:
	"""
	Each artefact can have different fields that uniquely determine
	its location in a storage. The key generator is common for all
	implementations of a storage.

	This class is an abstract class that needs to be implemented for
	each artefact. Each artefact storage will then use the key generator
	to generate a key for a given artefact.
	"""
	def generate(self, data):
		"""extract fields from an artefact uniquely determining its storage location"""
		raise NotImplementedError

