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

	def value2key(self, value, delimiter, key, key_order):
		if type(value) in [type(""), type(u"")]:
			return value

		if type(value) != type({}):
			raise ValueError("Second level key is not dictionary")

		keys = []
		for vkey in key_order[key]:
			if vkey not in value:
				raise ValueError("%s key missing" % vkey)

			if type(value[vkey]) != type("") and type(value[vkey]) != type(u""):
				raise ValueError("Second level value is not string")

			keys.append(value[vkey])

		return delimiter.join(keys)

