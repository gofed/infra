from infra.system.resources.garbagecollector import GarbageCollector
from infra.system.config.config import InfraConfig

if __name__ == "__main__":
	GarbageCollector(InfraConfig().resourceClientDirectory()).run()

