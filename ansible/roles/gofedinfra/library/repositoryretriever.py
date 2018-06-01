#!/usr/bin/python

DOCUMENTATION = '''
---
module: repositoryretriever
short_description: Retrieve your favorite repository
'''

EXAMPLES = '''
- name: Retrieve repository
  repositoryretriever:
    repository: github.com/kr/pretty
  register: result
'''

from ansible.module_utils.basic import *
from gofedlib.providers.providerbuilder import ProviderBuilder
from git import Repo
import hglib
from hglib.util import b

class RepositoryRetriever(object):

    def __init__(self, repository, repo_dir = ""):

        provider = ProviderBuilder().buildUpstreamWithLocalMapping()
        provider.parse(repository)

        self._repository = provider.signature()
        self._repo_dir = repo_dir

    def retrieve(self):
        self._repo_dir = tempfile.mkdtemp()
        if self._repository["provider"] == "github":
            clone_url = "https://github.com/%s/%s" % (self._repository["username"], self._repository["project"])
            Repo.clone_from(clone_url, self._repo_dir)
        elif self._repository["provider"] == "bitbucket":
            clone_url = "https://bitbucket.org/%s/%s" % (self._repository["username"], self._repository["project"])
            hglib.clone(b(clone_url), b(self._repo_dir))
        else:
            raise ValueError("Unknown repo: %s" % self._repository["provider"])

        return self

    def repository(self):
        return self._repository

    def repodir(self):
        return self._repo_dir


def main():

    fields = {
        "repository": {"required": True, "type": "str"},
        "directory": {"required": False, "type": "str"},
    }

    module = AnsibleModule(argument_spec=fields)

    r = RepositoryRetriever(module.params["repository"], repo_dir=module.params["directory"])
    failed = False
    errmsg = ""
    try:
        r.retrieve()
    except ValueError as err:
        failed = True
        errmsg = err

    result = dict(
        repository=r.repository(),
        directory=r.repodir(),
        changed=True,
    )

    if failed:
        module.fail_json(msg=errmsg, **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
