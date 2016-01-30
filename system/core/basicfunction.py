class BasicFunction:
	"""

	"""
	def __init__(self, obj):
		"""Set instance of a plugin. Each class of the instance must implement MetaProcessor class

		:param obj: instance of MetaProcessor class
		:type  obj: obj
		"""
		self.obj = obj

	def call(self, data):
		"""Forward data to correct methods of obj instance

		:type data: data to forward to a plugin
		"""

		# TODO(jchaloup): retrieve resource from resource client
		if not self.obj.setData(data):
			# TODO(jchaloup): return error or raise exception?
			return {}

		if not self.obj.execute():
			# TODO(jchaloup): return error or raise exception?
			return {}

		return self.obj.getData()
		
