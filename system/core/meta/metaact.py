from system.helpers.schema_validator import SchemaValidator
from system.core.functions.functionfactory import FunctionFactory

class MetaAct:
	"""
	Abstract class for all acts.
	Act is an implementation of one request handeling.
	E.g.
	  1. get data from a db,
	  2. send them to analysis,
	  3. send result to another analysis
	  4. commit transformations
	  5. store data to db or send the result in response

	https://github.com/gofed/infra/issues/11

	TODO:
	[  ] - specify request and response for each act
	"""

	def __init__(self, schema):
		self.schema = schema
		self.ff = FunctionFactory()

	def process(self):
		"""Implementation of request handler"""
		"""Thus should be automatically generated from act declaration"""
		raise NotImplementedError

		# get data d from a storage
		# get function f from a factory
		# r = f(d)
		# ...

		# in a simple case, only a sequence
		# in a complex case, acyclic oriented graph with only one leaf?

	def setRequest(self, data):
		"""Put data into act?"""
		"""TODO: how to put data into act? Can there be something general?"""
		raise NotImplementedError

	def getResponse(self):
		"""Get data from act?"""
		"""TODO: how to get data from act? Is this general enough?"""
		raise NotImplementedError

	def _validateInput(self, data):
		return SchemaValidator().validateFromFile(
			self.schema,
			data
		)
