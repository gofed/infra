#!/usr/bin/python

from ansible.module_utils.basic import *
from gofedinfra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA
from gofedlib.providers.providerbuilder import ProviderBuilder
from gofedlib.go.contentmetadataextractor import ContentMetadataExtractor


class GoProjectContentMetadataExtractor(object):

    def __init__(self, directory, repository="", hexsha=""):
        self._directory = directory

        provider = ProviderBuilder().buildUpstreamWithLocalMapping()
        provider.parse(repository)

        self._repository = provider.signature()
        self._hexsha = hexsha

        self._metadata = {}

    def extract(self):
        contentmetadataextractor = ContentMetadataExtractor(self._directory)
        contentmetadataextractor.extract()
        data = contentmetadataextractor.projectContentMetadata()
        self._metadata = data["metadata"]

    def golangProjectContentMetadataArtefact(self):
        return {
            "artefact": ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA,
            "repository": self._repository,
            "commit": self._hexsha,
            "metadata": self._metadata
        }


def main():

    fields = {
        "directory": {"required": True, "type": "str"},
        "repository": {"required": False, "type": "str", "default": ""},
        "hexsha": {"required": False, "type": "str", "default": ""},
    }

    module = AnsibleModule(argument_spec=fields)

    e = GoProjectContentMetadataExtractor(
        module.params["directory"],
        repository=module.params["repository"],
        hexsha=module.params["hexsha"],
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
        repository=module.params["repository"],
        hexsha=module.params["hexsha"],
        artefacts={
            ARTEFACT_GOLANG_PROJECT_CONTENT_METADATA: e.golangProjectContentMetadataArtefact(),
        },
        changed=True,
    )

    if failed:
        module.fail_json(msg=errmsg, **result)

    module.exit_json(**result)


if __name__ == '__main__':
    main()
