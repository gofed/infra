from .actfactory import ActFactory

class FakeActFactory(ActFactory):

	def __init__(self):
		ActFactory.__init__(self)

	def bake(self, item_ID):
		return ActFactory.bake(self, "fake-%s" % item_ID)

