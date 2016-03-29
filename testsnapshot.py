from system.models.snapshots.reconstructor import SnapshotReconstructor
import logging
#logging.basicConfig(level=logging.INFO)
import json

if __name__ == "__main__":

	repository = {
		"provider": "github",
		"username": "coreos",
		"project": "etcd"
	}

	commit = "5e6eb7e19d6385adfabb1f1caea03e732f9348ad"
	ipprefix = "github.com/coreos/etcd"

	print json.dumps(SnapshotReconstructor().reconstruct(repository, commit, ipprefix).snapshot().Godeps())
