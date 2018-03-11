#!/usr/bin/python

from ansible.module_utils.basic import *
from gofedlib.go.symbolsextractor import extractor
from gofedlib.types import ExtractionError
from gofedinfra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES, ARTEFACT_GOLANG_PROJECT_EXPORTED_API
from gofedlib.providers.providerbuilder import ProviderBuilder

class GoSymbolsExtractor(object):

    def __init__(self, directory, repository={}, hexsha="", ipprefix=""):
        self._directory = directory

        provider = ProviderBuilder().buildUpstreamWithLocalMapping()
        provider.parse(repository)

        self._repository = provider.signature()
        self._hexsha = hexsha
        self._ipprefix = ipprefix

        self._packages = {}
        self._exported_api = []

    def extract(self):
        e = extractor.GoSymbolsExtractor(
            self._directory,
        )
        e.extract()

        self._packages = e.packages()
        self._exported_api = e.exportedApi()

    def golangProjectPackagesArtefact(self):
        return {
            "artefact": ARTEFACT_GOLANG_PROJECT_PACKAGES,
            "repository": self._repository,
            "commit": self._hexsha,
            "ipprefix": self._ipprefix,
            "data": self._packages,
        }

    def golangProjectExportedAPI(self):
        return {
            "artefact": ARTEFACT_GOLANG_PROJECT_EXPORTED_API,
            "repository": self._repository,
            "commit": self._hexsha,
            "packages": self._exported_api,
        }

    def repository(self):
        return self._repository


def main():

    fields = {
        "directory": {"required": True, "type": "str"},
        "repository": {"required": False, "type": "str"},
        "hexsha": {"required": False, "type": "str"},
        "ipprefix": {"required": False, "type": "str"},
    }

    module = AnsibleModule(argument_spec=fields)

    e = GoSymbolsExtractor(
        module.params["directory"],
        repository=module.params["repository"],
        hexsha=module.params["hexsha"],
        ipprefix=module.params["ipprefix"],
    )
    failed = False
    errmsg = ""

    try:
        e.extract()
    except ExtractionError as err:
        failed = True
        errmsg = err
    except OSError as err:
        failed = True
        errmsg = err

    result = dict(
        repository=e.repository(),
        hexsha=module.params["hexsha"],
        ipprefix=module.params["ipprefix"],
        artefacts={
            ARTEFACT_GOLANG_PROJECT_PACKAGES: e.golangProjectPackagesArtefact(),
            ARTEFACT_GOLANG_PROJECT_EXPORTED_API: e.golangProjectExportedAPI(),
        },
        changed=True,
    )

    if failed:
        module.fail_json(msg=errmsg, **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
