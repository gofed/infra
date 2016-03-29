from system.models.snapshots.reconstructor import SnapshotReconstructor
import logging
logging.basicConfig(level=logging.INFO)
import json

if __name__ == "__main__":

	repository = {
		"provider": "github",
		"username": "coreos",
		"project": "etcd"
	}

	commit = "5e6eb7e19d6385adfabb1f1caea03e732f9348ad"
	ipprefix = "github.com/coreos/etcd"

	snapshot = SnapshotReconstructor().reconstruct(repository, commit, ipprefix, mains = ["main.go", "etcdctl/main.go"], tests=True).snapshot()

	print ""
	print json.dumps(snapshot.Godeps())
	print ""
	print snapshot.GLOGFILE()
