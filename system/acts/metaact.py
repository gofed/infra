class MetaAct:

	def setData(self, data):
		"""Validation and data pre-processing"""
		raise NotImplementedError

	def getData(self):
		"""Validation and data post-processing"""
		raise NotImplementedError

	def execute(self):
		"""Impementation of concrete data processor"""
		raise NotImplementedError
