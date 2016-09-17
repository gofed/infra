from .garbagecollector import GarbageCollector
from infra.system.config.config import InfraConfig

class ResourceClientGC(GarbageCollector):

	def __init__(self, verbose=False):
		GarbageCollector.__init__(self,
			InfraConfig().resourceClientDirectory(),
			verbose=verbose
		)

