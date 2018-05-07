#!/usr/bin/python

from ansible.module_utils.basic import *
from gofedlib.go.apiextractor import extractor
from gofedlib.providers.providerbuilder import ProviderBuilder
import json
import StringIO
import gzip
import base64

class ApiExtractor(object):

    def __init__(self, gopath, generated, package_path, hexsha, depsfile, cgodir = ""):
        self._extractor = extractor.ApiExtractor(gopath, generated, package_path, hexsha, depsfile, cgodir)
        self._generated = generated
        self._api_artefacts = []
        self._contract_artefacts = []
        self._static_alloc_artefacts = []

    def extract(self):
        self._extractor.extract()
        self._generateArtefacts()
        return self

    def _dict2gzip(self, dict):
        fd = StringIO.StringIO()
        gz = gzip.GzipFile(fileobj=fd, mode="w")
        gz.write(json.dumps(dict))
        gz.close()
        data = fd.getvalue()
        fd.close()
        return base64.b64encode(data)


    def _generateArtefacts(self):
        self._api_artefacts = []
        self._contract_artefacts = []
        self._static_alloc_artefacts = []
        up = ProviderBuilder().buildUpstreamWithLocalMapping()
        gl = len(self._generated)
        for root, dirs, files in os.walk(self._generated):
            if root.startswith(os.path.join(self._generated, "golang")):
                continue

            # TODO(jchaloup): generate artefacts in parallel
            for file in filter(lambda f: f.endswith(".json"), files):

                if file != "contracts.json" and file != "api.json" and file != "allocated.json":
                    continue

                ipp_hexsha = root[gl + 1:]
                hexsha = os.path.basename(ipp_hexsha)
                ipprefix = os.path.dirname(ipp_hexsha)
                with open(os.path.join(root, file), "r") as fp:
                    data = json.load(fp)

                artefact = {
                    "ipprefix": ipprefix,
                    # Repository of origin
                    "project": up.parse(ipprefix).prefix(),
                    "hexsha": hexsha,
                    "data": data,
                }

                if file == "api.json":
                    # The list of all packages for a given project is
                    # stored in golang-project-packages artefact
                    # So it's ok to use the ipprefix as a part of the api artefact key
                    artefact["artefact"] = "golang-project-api"
                    self._api_artefacts.append(self._dict2gzip(artefact))
                    continue

                if file == "contracts.json":
                    artefact["artefact"] = "golang-project-contracts"
                    self._contract_artefacts.append(self._dict2gzip(artefact))
                    continue

                if file == "allocated.json":
                    artefact["artefact"] = "golang-project-static-allocations"
                    self._contract_artefacts.append(self._dict2gzip(artefact))
                    continue

    def apiArtefacts(self):
        return self._api_artefacts

    def contractArtefacts(self):
        return self._contract_artefacts

    def statisAllocationArtefacts(self):
        return self._static_alloc_artefacts

def main():

    fields = {
        "gopath": {"required": True, "type": "str"},
        "generated": {"required": True, "type": "str"},
        "package_path": {"required": True, "type": "str"},
        "hexsha": {"required": True, "type": "str"},
        "depsfile": {"required": True, "type": "str"},
        "cgodir": {"required": False, "type": "str", "default": ""},
    }

    module = AnsibleModule(argument_spec=fields)

    e = ApiExtractor(
        gopath=module.params["gopath"],
        generated=module.params["generated"],
        package_path=module.params["package_path"],
        hexsha=module.params["hexsha"],
        depsfile=module.params["depsfile"],
        cgodir=module.params["cgodir"],
    )

    failed = False
    errmsg = ""

    try:
        e.extract()
    except extractor.ExtractionException as err:
        failed = True
        errmsg = err

    result = dict(
        package_path=module.params["package_path"],
        hexsha=module.params["hexsha"],
        artefacts={
            "golang-project-api": e.apiArtefacts(),
            "golang-project-contracts": e.contractArtefacts(),
            "golang-project-static-allocations": e.statisAllocationArtefacts(),
        },
        changed=True,
    )

    if failed:
        module.fail_json(msg=errmsg, **result)

    module.exit_json(**result)

if __name__ == '__main__':
    main()
