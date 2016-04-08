from gofed_resources.proposal.rpmretriever import RpmRetriever
from gofed_resources.proposal.gitrepositoryretriever import GitRepositoryRetriever

from gofed_resources.proposal.providerbuilder import ProviderBuilder
from gofed_resources.proposal.mercurialrepositoryretriever import MercurialRepositoryRetriever

from gofed_lib.pkgdb.client import PkgDBClient, FakePkgDBClient
from gofed_lib.kojiclient import KojiClient
import json

if __name__ == "__main__":
	#print RpmRetriever().retrieve("Fedora", "f24", "etcd-2.2.4-2.fc24", "etcd-devel-2.2.4-2.fc24.noarch.rpm")
	#print GithubRepositoryRetriever().retrieve("coreos", "etcd")

	#provider = ProviderBuilder().buildGithubRepositoryProvider()
	#print provider.provide("coreos", "etcd")

	#print MercurialRepositoryRetriever().retrieve({"provider": "bitbucket", "username": "ww", "project": "goautoneg"})

	#print PkgDBClient().packageExists("golang-github-coreos-common")
	#print json.dumps(FakePkgDBClient().getGolangPackages())

	print KojiClient().getPackageBuilds("f24", "golang-bitbucket-ww-goautoneg")
