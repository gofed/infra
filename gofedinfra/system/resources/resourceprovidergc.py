from infra.system.resources.garbagecollector import GarbageCollector
from gofedresources.config.config import ResourcesConfig

class ResourceProviderGC(GarbageCollector):

	def __init__(self, verbose=False):
		GarbageCollector.__init__(self,
			ResourcesConfig().providerDirectory(),
			verbose=verbose
		)

