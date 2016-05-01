from infra.system.resources.garbagecollector import GarbageCollector
from gofed_resources.proposal.config.config import ResourcesConfig

if __name__ == "__main__":
	GarbageCollector(ResourcesConfig().providerDirectory()).run()

