from .garbagecollector import GarbageCollector
from infra.system.config.config import InfraConfig

class ResourceClientGC(GarbageCollector):

	def __init__(self):
		GarbageCollector.__init__(self,
			InfraConfig().resourceClientDirectory()
		)

