from gofed_resources.proposal.rpmretriever import RpmRetriever
from gofed_resources.proposal.gitrepositoryretriever import GitRepositoryRetriever

from gofed_resources.proposal.providerbuilder import ProviderBuilder
from gofed_resources.proposal.mercurialrepositoryretriever import MercurialRepositoryRetriever

if __name__ == "__main__":
	#print RpmRetriever().retrieve("Fedora", "f24", "etcd-2.2.4-2.fc24", "etcd-devel-2.2.4-2.fc24.noarch.rpm")
	#print GithubRepositoryRetriever().retrieve("coreos", "etcd")

	#provider = ProviderBuilder().buildGithubRepositoryProvider()
	#print provider.provide("coreos", "etcd")

	print MercurialRepositoryRetriever().retrieve({"provider": "bitbucket", "username": "ww", "project": "goautoneg"})
