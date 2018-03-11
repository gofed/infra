#!/usr/bin/python

DOCUMENTATION = '''
---
module: repositorycoderetriever
short_description: Retrieve source code from your favorite repository
'''

EXAMPLES = '''
- name: Retrieve source code from a repository by commit
  repositorycoderetriever:
    repository: github.com/coreos/etcd
    hexsha: 121edf0467052d55876a817b89875fb39a99bf78
  register: result
'''

from ansible.module_utils.basic import *
from gofedlib.providers.providerbuilder import ProviderBuilder
from gofedlib.urlbuilder.builder import UrlBuilder
import urllib2
import tempfile
import tarfile
import os


class ResourceUnableToRetrieveError(Exception):
    pass


class RepositoryCodeRetriever(object):

    def __init__(self, repository, hexsha=""):

        provider = ProviderBuilder().buildUpstreamWithLocalMapping()
        provider.parse(repository)

        self._repository = provider.signature()
        self._hexsha = hexsha
        self._code_dir = ""

    def retrieve(self):
        tarball_file = self._retrieveTarball()
        self._code_dir = self._extractTarball(tarball_file)
        os.remove(tarball_file)
        return

    def _retrieveTarball(self):
        if self._repository["provider"] == "github":
            return self._retrieveResource(
                UrlBuilder().buildGithubSourceCodeTarball(
                    self._repository["username"],
                    self._repository["project"],
                    self._hexsha,
                )
            )

        if self._repository["provider"] == "bitbucket":
            return self._retrieveResource(
                UrlBuilder().buildBitbucketSourceCodeTarball(
                    self._repository["username"],
                    self._repository["project"],
                    self._hexsha,
                )
            )

        raise KeyError("Provider '%s' not supported" % self._repository["provider"])

    def _retrieveResource(self, resource_url):
        # TODO(jchaloup): catch exceptions: urllib2.URLError, urllib2.HTTPError
        #    raise ResourceNotRetrieved instead?
        try:
            response = urllib2.urlopen(resource_url)
        except urllib2.URLError as err:
            # can a user do something about it?
            msg = "Unable to retrieve resource, url = %s, err = %s" % (resource_url, err)
            raise urllib2.URLError(msg)
        except urllib2.HTTPError as err:
            # can a user do something about it?
            msg = "Unable to retrieve resource, url = %s, err = %s" % (resource_url, err)
            raise urllib2.HTTPError(msg)

        try:
            with tempfile.NamedTemporaryFile(delete=False) as f:
                f.write(response.read())
                f.flush()
        except IOError as e:
            # can a user do something about it?
            msg = "Unable to store retrieved resource, err = " % (err)
            raise ResourceUnableToRetrieveError(msg)

        return f.name

    def _extractTarball(self, resource_location):
        tar = tarfile.open(resource_location)
        dirpath = tempfile.mkdtemp()
        tar.extractall(dirpath)
        rootdir = ""
        for member in tar.getmembers():
            rootdir = member.name.split("/")[0]
            break
        tar.close()

        return os.path.join(dirpath, rootdir)

    def repository(self):
        return self._repository

    def codedir(self):
        return self._code_dir


def main():

    fields = {
        "repository": {"required": True, "type": "str"},
        "hexsha": {"required": True, "type": "str"},
        # "version": {"required": False, "type": "str" },
        # "tag": {"required": False, "type": "str" },
        "directory": {"required": False, "type": "str"},
    }

    module = AnsibleModule(argument_spec=fields)

    r = RepositoryCodeRetriever(module.params["repository"], hexsha=module.params["hexsha"])
    failed = False
    errmsg = ""
    try:
        r.retrieve()
    except urllib2.URLError as err:
        failed = True
        errmsg = err
    except urllib2.HTTPError as err:
        failed = True
        errmsg = err
    except ResourceUnableToRetrieveError as err:
        failed = True
        errmsg = err

    result = dict(
        repository=r.repository(),
        directory=r.codedir(),
        changed=True,
    )

    if failed:
        module.fail_json(msg=errmsg, **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
