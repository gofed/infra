#!/usr/bin/python

from ansible.module_utils.basic import *

import tempfile
import os
from gofedlib.utils import runCommand
import json

class GoList(object):

    def __init__(self, package_path, gopath, artefact_prefix, artefact_key, ignore_dirs, ignore_trees, ignore_regexs, all_deps, provided, imported, skip_self, tests, show_main, to_install, include_extensions):

        self._package_path = package_path
        self._gopath = gopath
        self._ignore_dirs = ignore_dirs
        self._ignore_trees = ignore_trees
        self._ignore_regexs = ignore_regexs
        self._all_deps = all_deps
        self._provided = provided
        self._imported = imported
        self._tests = tests
        self._show_main = show_main
        self._to_install = to_install
        self._skip_self = skip_self
        self._include_extensions = include_extensions
        self._artefact_prefix = artefact_prefix
        self._artefact_key = artefact_key

        self._artefact = {}

    def list(self):
        options = {
            "package-path": self._package_path,
            "json": "true"
        }

        so, se, rc = runCommand("GOPATH={} golist {}".format(self._gopath, " ".join(map(lambda l: "--{}={}".format(l, options[l]), options))))
        if rc != 0:
            raise ValueError("golist unzero return code=%{}: %{}".format(rc, se))

        self._artefact = {
            "artefact": "{}-packages".format(self._artefact_prefix),
            "data": json.loads(so),
        }

        for key in self._artefact_key:
            self._artefact[key] = self._artefact_key[key]

        return self

    def packagesArtefact(self):
        return self._artefact

def main():

    fields = {
        "package-path": {"required": True, "type": "str"},
        "gopath": {"required": True, "type": "str"},
        "artefact": {"required": True, "type": "dict"},
        "ignore-dirs": {"required": False, "type": "list"},
        "ignore-trees": {"required": False, "type": "list"},
        "ignore-regexs": {"required": False, "type": "list"},
        "all-deps": {"required": False, "type": "bool"},
        "provided": {"required": False, "type": "bool"},
        "imported": {"required": False, "type": "bool"},
        "skip-self": {"required": False, "type": "bool"},
        "tests": {"required": False, "type": "bool"},
        "show-main": {"required": False, "type": "bool"},
        "to-install": {"required": False, "type": "bool"},
        "include-extensions": {"required": False, "type": "list"},
    }

    module = AnsibleModule(argument_spec=fields)

    if "prefix" not in module.params["artefact"]:
        module.fail_json(msg="artefact argument missing prefix field")

    if "key" not in module.params["artefact"]:
        module.fail_json(msg="artefact argument missing key field")

    if type({}) != type(module.params["artefact"]["key"]):
        module.fail_json(msg="artefact.key field is not a dictionary")

    for key in module.params["artefact"]["key"]:
        if type("") != type(module.params["artefact"]["key"][key]):
            module.fail_json(msg="artefact.key is not a simple dictionary")

    gl = GoList(
        package_path = module.params["package-path"],
        gopath = module.params["gopath"],
        artefact_prefix = module.params["artefact"]["prefix"],
        artefact_key = module.params["artefact"]["key"],
        ignore_dirs = module.params["ignore-dirs"],
        ignore_trees = module.params["ignore-trees"],
        ignore_regexs = module.params["ignore-regexs"],
        all_deps = module.params["all-deps"],
        provided = module.params["provided"],
        imported = module.params["imported"],
        skip_self = module.params["skip-self"],
        tests = module.params["tests"],
        show_main = module.params["show-main"],
        to_install = module.params["to-install"],
        include_extensions = module.params["include-extensions"]
    )

    failed = False
    errmsg = ""
    try:
        artefact = gl.list().packagesArtefact()
    except ValueError as err:
        failed = True
        errmsg = err

    result = dict(
        gopath=module.params["gopath"],
        artefact=artefact,
        changed=True,
    )

    if failed:
        module.fail_json(msg=errmsg, **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
