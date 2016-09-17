import optparse
import logging
import re
import json

from gofedlib.kojiclient import FakeKojiClient, KojiClient
from gofedlib.pkgdb.client import FakePkgDBClient
from gofedlib.distributionsnapshot import DistributionSnapshot
from gofedlib.eco.capturer import EcoCapturer
from infra.system.models.ecosnapshots.distributionsnapshotchecker import DistributionSnapshotChecker

#logging.basicConfig(level=logging.INFO)

def setOptions():

	parser = optparse.OptionParser("%prog [-l] [-v] [Godeps.json]")

	parser.add_option(
	    "", "-v", "--verbose", dest="verbose", action = "store_true", default = False,
	    help = "Verbose mode"
	)

	parser.add_option(
	    "", "", "--target", dest="target", default = "Fedora:rawhide",
	    help = "Target distribution in a form OS:version, e.g. Fedora:f24. Implicitly set to Fedora:rawhide"
	)

	parser.add_option(
	    "", "", "--custom-packages", dest="custompackages", default = "",
	    help = "Comma separated string of golang packages not prefixed with golang-*, e.g. etcd,runc"
	)

	return parser

if __name__ == "__main__":
	options, args = setOptions().parse_args()

	distributions = []
	for distro in options.target.split(","):
		parts = distro.split(":")
		distributions.append({"product": parts[0], "version": parts[1]})

	custom_packages = options.custompackages.split(",")

	koji_client = KojiClient()
	pkgdb_client = FakePkgDBClient()

	# TODO(jchaloup):
	# - where to store snapshots? under gofedlib or gofed_infra? I am inclined to use gofed_data to store all artefacts and other data kinds
	#   as each snapshot is determined by timestamp, it can not be stored as artefacts are (without introducing additional list of snashots)
	#   Other thought (once the storage can provide a list of artefact based on a partial key, repo artefact and cache can be regenerated
	#   based on commits in a storage rather then on a list of commits retrieved from repository.
	#   Temporary, save the snapshot into db (generated artefact for it) and always replace distribution artefact with the latest snapshot.
	#   Once the storage provides list functionality, just retrieve the snapshot with the biggest timestamp (for given distribution).
	# - introduce EcoScannerAct updating the latest snapshot and scan of the new rpms. Later, add support for upstream repositories as well.
	#

	checker = DistributionSnapshotChecker(koji_client, pkgdb_client)
	checker.check(distributions, custom_packages, full_check=True)


