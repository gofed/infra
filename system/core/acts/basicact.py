from types import ActFailedError

class BasicAct:
	"""Wrapper for basic acts.
	Basic act locally accessed act.
	"""

	def __init__(self, obj):
		self.obj = obj

	def call(self, data):
		if not self.obj.setData(data):
			raise ValueError("Invalid input: %s" % data)

		if not self.obj.execute():
			raise ActFailedError("Act %s failed" % self.__name__)

		return self.obj.getData()
