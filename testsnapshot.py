from gofedinfra.system.models.snapshots.reconstructor import SnapshotReconstructor
from gofedinfra.system.models.snapshots.checker import SnapshotChecker
import logging
logging.basicConfig(level=logging.INFO)
import json

from gofedlib.go.snapshot import Snapshot
from gofedlib.distribution.distributionsnapshot import DistributionSnapshot
from gofedlib.distribution.clients.pkgdb.client import FakePkgDBClient
from gofedlib.distribution.clients.koji.client import FakeKojiClient, KojiClient

def test_reconstructor():
	#repository = {
	#	"provider": "github",
	#	"username": "coreos",
	#	"project": "etcd"
	#}

	#commit = "5e6eb7e19d6385adfabb1f1caea03e732f9348ad"
	#ipprefix = "github.com/coreos/etcd"

	repository = {
		"provider": "github",
		"username": "influxdb",
		"project": "influxdb"
	}

	commit = "da1b59e7d7764d36786253b2db13b97f42ed4e1d"
	ipprefix = "github.com/influxdb/influxdb"

	#snapshot = SnapshotReconstructor().reconstruct(repository, commit, ipprefix, mains = ["main.go", "etcdctl/main.go"], tests=True).snapshot()
	snapshot = SnapshotReconstructor().reconstruct(repository, commit, ipprefix, mains = [], tests=True).snapshot()


	print ""
	print json.dumps(snapshot.Godeps())
	print ""
	print snapshot.GLOGFILE()

if __name__ == "__main__":

	test_reconstructor()

	exit(1)

	s1 = DistributionSnapshot().load("/home/jchaloup/Projects/gofed/infra/snapshot1.json")
	s2 = DistributionSnapshot().load("/home/jchaloup/Projects/gofed/infra/snapshot2.json")

	data = s2.compare(s1)
	print data["new_rpms"]

	exit(1)
	snapshot = DistributionSnapshot("rawhide", "1.5")

	client = FakePkgDBClient()
	kojiclient = FakeKojiClient()

	packages = client.getGolangPackages()
	for package in packages:
		try:
			data = kojiclient.getLatestRPMS("rawhide", package)
		except KeyError as e:
			print e
			continue
		snapshot.setRpms(package, data["rpms"])

	print json.dumps(snapshot.json())

	exit(1)

	file = "/home/jchaloup/Packages/etcd/fedora/etcd/etcd-5e6eb7e19d6385adfabb1f1caea03e732f9348ad/Godeps/Godeps.json"

	snapshot = Snapshot()
	snapshot.readGodepsFile(file)

	SnapshotChecker().check(snapshot, "Fedora", "rawhide")

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
