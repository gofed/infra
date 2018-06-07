#!/usr/bin/python

from ansible.module_utils.basic import *

import tempfile
import os
from gofedlib.utils import runCommand
import json

class GoBuild(object):

    def __init__(self, package_path, gopath, library=False):

        self._package_path = package_path
        self._gopath = gopath
        self._library = library

        self._status = {}

    def build(self):
        options = {
            "package-path": self._package_path,
            "provided": "true"
        }

        # Check all provided packages (no mains, no tests)
        so, se, rc = runCommand("GOPATH={} golist --package-path {} --provided".format(self._gopath, self._package_path))
        if rc != 0:
            raise ValueError("golist non-zero return code=%{}: %{}".format(rc, se))

        packages = filter(lambda l: l.startswith(self._package_path), so.split("\n"))
        self._packages = packages

        f = tempfile.NamedTemporaryFile()

        for package in packages:
            so, se, rc = runCommand("GOPATH={} go build -o {} --buildmode=archive {}".format(self._gopath, f.name, package))
            if rc != 0:
                self._status[package] = {
                    "built": False,
                    "reason": se,
                }
            else:
                self._status[package] = {
                    "built": True,
                }

        f.close()

        return self

    def status(self):
        return self._status


def main():

    fields = {
        "package-path": {"required": True, "type": "str"},
        "gopath": {"required": True, "type": "str"},
        "library": {"required": False, "type": "bool", "default": False},
    }

    module = AnsibleModule(argument_spec=fields)

    gb = GoBuild(
        package_path = module.params["package-path"],
        gopath = module.params["gopath"],
        library = module.params["library"],
    )

    failed = False
    errmsg = ""
    try:
        status = gb.build().status()
    except ValueError as err:
        failed = True
        errmsg = err

    result = dict(
        gopath=module.params["gopath"],
        status=status,
        changed=True,
    )

    if failed:
        module.fail_json(msg=errmsg, **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
