from infra.system.resources.garbagecollector import GarbageCollector

if __name__ == "__main__":
	GarbageCollector("/var/lib/gofed/resource_client").run()

