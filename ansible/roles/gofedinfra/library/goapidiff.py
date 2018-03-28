#!/usr/bin/python

from ansible.module_utils.basic import *
from gofedlib.go.apidiff import apidiff
from gofedinfra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECTS_API_DIFF

"""
Input:
- exported API of a project for a given commit1
- exported API of a project for a given commit2
E.g.
{"exported_api_1": JSON, "exported_api_2": JSON}
Output:

Algorithm:
- both APIs must be of the same project

api_2 is new
api_1 is old

Result of comparison is new - old, i,e, api_2 - api_1
"""

class GoApiDiff(object):

    def __init__(self, exported_api_1, exported_api_2):
        self._exported_api1 = exported_api_1
        self._exported_api2 = exported_api_2

        self._api_diff = {}
        self._repository = ""
        self._commit1 = ""
        self._commit2 = ""

    def _generateGolangProjectsAPIDiffArtefact(self):
        return {
            "artefact": ARTEFACT_GOLANG_PROJECTS_API_DIFF,
            "repository": self._repository,
            "commit1": self._commit1,
            "commit2": self._commit2,
            "data": self._apidiff
        }

    def extract(self):
        # TODO(jchaloup): make sure the GoApiDiff throws
        # exception when repositories of both APIs are different!!!
        self._apidiff = apidiff.GoApiDiff(
            self._exported_api1["packages"],
            self._exported_api2["packages"],
        ).runDiff().apiDiff()

        self._repository = self._exported_api1["repository"]
        self._commit1 = self._exported_api1["commit"]
        self._commit2 = self._exported_api2["commit"]

    def golangProjectsApiDiffArtefact(self):
        return {
            "artefact": ARTEFACT_GOLANG_PROJECTS_API_DIFF,
            "repository": self._exported_api1["repository"],
            "commit1": self._exported_api1["commit"],
            "commit2": self._exported_api1["commit"],
            "data": self._apidiff
        }

    def repository(self):
        return self._repository

    def commit1(self):
        return self._commit1

    def commit2(self):
        return self._commit2

def main():

    fields = {
        "exported_api_1": {"required": True, "type": "dict"},
        "exported_api_2": {"required": True, "type": "dict"},
    }

    module = AnsibleModule(argument_spec=fields)

    e = GoApiDiff(
        exported_api_1=module.params["exported_api_1"],
        exported_api_2=module.params["exported_api_2"],
    )
    failed = False
    errmsg = ""

    try:
        e.extract()
    except ValueError as err:
        failed = True
        errmsg = err

    result = dict(
        repository=e.repository(),
        commit1=e.commit1(),
        commit2=e.commit2(),
        artefacts={
            ARTEFACT_GOLANG_PROJECTS_API_DIFF: e.golangProjectsApiDiffArtefact(),
        },
        changed=True,
    )

    if failed:
        module.fail_json(msg=errmsg, **result)

    module.exit_json(**result)

if __name__ == '__main__':
    main()
