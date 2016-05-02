from infra.system.resources.garbagecollector import GarbageCollector
from gofed_resources.proposal.config.config import ResourcesConfig

class ResourceProviderGC(GarbageCollector):

	def __init__(self):
		GarbageCollector.__init__(self,
			ResourcesConfig().providerDirectory()
		)

