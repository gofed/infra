from .functionfactory import FunctionFactory
from infra.system.resources.client import ResourceClient
from infra.system.resources.fakeresourcehandler import FakeResourceHandler

class FakeFunctionFactory(FunctionFactory):

	def __init__(self):
		FunctionFactory.__init__(self)

	def bake(self, function_ID):
		c = ResourceClient(None, "")
		c._resource_handler = FakeResourceHandler(None, "")

		function = FunctionFactory.bake(self, "fake%s" % function_ID)
		function._resource_client = c
		return function
