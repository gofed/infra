from infra.system.plugins.simplefilestorage.artefactdriverfactory import ArtefactDriverFactory as FileFactory
from infra.system.plugins.simpleetcdstorage.artefactdriverfactory import ArtefactDriverFactory as EtcdFactory

from infra.system.artefacts import artefacts

if __name__ == "__main__":

	data = {
		"artefact": artefacts.ARTEFACT_GOLANG_PROJECT_INFO_FEDORA,
		"distribution": "rawhide",
		"project": "github.com/coreos/etcd",
		"commit": "3i4u3iu4i2u34o244324",
		"last-updated": "2016-04-03"
	}

	driver = EtcdFactory().build(artefacts.ARTEFACT_GOLANG_PROJECT_INFO_FEDORA)
	driver.store(data)
	#print driver.retrieve(data)
