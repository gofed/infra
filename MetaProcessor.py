class MetaProcessor:
	"""
	Abstract class that each analysis, extractor
	and other kind must re-implement.

	https://github.com/gofed/infra/issues/8
	"""

	def setData(self, data):
		"""Validation and data pre-processing"""
		raise NotImplementedError

	def getData(self, data):
		"""Validation and data post-processing"""
		raise NotImplementedError

	def execute(self):
		"""Impementation of concrete data processor"""
		raise NotImplementedError


