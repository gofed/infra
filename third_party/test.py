from gofed_resources.proposal.rpmretriever import RpmRetriever
from gofed_resources.proposal.githubrepositoryretriever import GithubRepositoryRetriever

from gofed_resources.proposal.providerbuilder import ProviderBuilder

if __name__ == "__main__":
	#print RpmRetriever().retrieve("Fedora", "f24", "etcd-2.2.4-2.fc24", "etcd-devel-2.2.4-2.fc24.noarch.rpm")
	#print GithubRepositoryRetriever().retrieve("coreos", "etcd")

	provider = ProviderBuilder().buildGithubRepositoryProvider()
	print provider.provide("coreos", "etcd")

