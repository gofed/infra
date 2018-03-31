#!/usr/bin/python

from ansible.module_utils.basic import *

import urllib2
import tempfile
import os
from gofedlib.utils import runCommand


class RpmRetriever(object):

    def __init__(self, product, distribution, build, rpm):

        self._product = product
        self._distribution = distribution
        self._build = build
        self._rpm = rpm

        self._rpm_dir = ""

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

    def _extractRpm(self, resource_location):
        # TODO(jchaloup): use python module (e.g. github.com/srossross/rpmfile)
        dirpath = tempfile.mkdtemp()
        cwd = os.getcwd()
        os.chdir(dirpath)
        so, se, rc = runCommand("rpm2cpio %s | cpio -idmv" % resource_location)
        if rc != 0:
            raise Exception("rpm2cpio error\nrc: {}\n se: {}\nso: {}".format(rc, se, so))
        os.chdir(cwd)

        return dirpath

    def retrieve(self):
        # get n,v,r from build
        parts = self._build.split("-")
        if len(parts) < 3:
            raise ValueError("Invalid build nvr: %s" % self._build)

        release = parts[-1]
        version = parts[-2]
        name = "-".join(parts[:-2])

        # get architecture
        parts = self._rpm.split(".")
        if len(parts) < 3:
            raise ValueError("Invalid rpm nvr.arch.(s)rpm: %s" % self._rpm)

        arch = parts[-2]

        # construct download url
        # https://kojipkgs.fedoraproject.org//packages/etcd/2.2.4/2.fc24/noarch/etcd-devel-2.2.4-2.fc24.noarch.rpm
        # https://kojipkgs.fedoraproject.org//packages/etcd/2.2.4/2.fc24/x86_64/etcd-unit-test-2.2.4-2.fc24.x86_64.rpm
        # https://kojipkgs.fedoraproject.org//packages/etcd/2.2.4/2.fc24/src/etcd-2.2.4-2.fc24.src.rpm
        rpm_url = "https://kojipkgs.fedoraproject.org/packages/%s/%s/%s/%s/%s" % (
            name, version, release, arch, self._rpm)

        rpmfile = self._retrieveResource(rpm_url)
        self._rpm_dir = self._extractRpm(rpmfile)
        try:
            os.remove(rpmfile)
        except OSError:
            pass

        return self

    def rpmdir(self):
        return self._rpm_dir


def main():

    fields = {
        "product": {"required": True, "type": "str"},
        "distribution": {"required": True, "type": "str"},
        "build": {"required": True, "type": "str"},
        "rpm": {"required": True, "type": "str"},
    }

    module = AnsibleModule(argument_spec=fields)

    r = RpmRetriever(
        product = module.params["product"],
        distribution=module.params["distribution"],
        build=module.params["build"],
        rpm=module.params["rpm"],
    )
    failed = False
    errmsg = ""
    try:
        r.retrieve()
    except ValueError as err:
        failed = True
        errmsg = err

    result = dict(
        build=module.params["build"],
        rpm=module.params["rpm"],
        directory=r.rpmdir(),
        changed=True,
    )

    if failed:
        module.fail_json(msg=errmsg, **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
