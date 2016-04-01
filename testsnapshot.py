from system.models.snapshots.reconstructor import SnapshotReconstructor
from system.models.snapshots.checker import SnapshotChecker
import logging
logging.basicConfig(level=logging.INFO)
import json

from gofed_lib.snapshot import Snapshot

if __name__ == "__main__":

	file = "/home/jchaloup/Packages/etcd/fedora/etcd/etcd-5e6eb7e19d6385adfabb1f1caea03e732f9348ad/Godeps/Godeps.json"

	snapshot = Snapshot()
	snapshot.readGodepsFile(file)

	SnapshotChecker().check(snapshot, "rawhide")

	exit(1)

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
