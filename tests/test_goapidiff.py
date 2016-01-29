import json
import os

import pytest

from system.tests.utils import ProjectID
from system.plugins.goapidiff.analyzer import GoApiDiff


CONFIG_FILE_NAME = 'goapidiff.json'


configuration = {}


def pytest_generate_tests(metafunc):
    path = os.path.dirname(os.path.realpath(__file__))
    configfile = os.path.join(path, CONFIG_FILE_NAME)
    try:
        with open(configfile, 'rb') as f:
            configuration.update(json.load(f))
    except IOError:
        raise RuntimeError(
            'Cannot load configuration from "{}"'.format(configfile))
    if 'pair_identical_commits' in metafunc.fixturenames:
        metafunc.parametrize(
            'pair_identical_commits', configuration['pairs_identical_commits'])
    if 'pair_different_projects' in metafunc.fixturenames:
        metafunc.parametrize(
            'pair_different_projects', configuration['pairs_different_projects'])
    if 'pair_generic' in metafunc.fixturenames:
        metafunc.parametrize('pair_generic', configuration['pairs_generic'])


class TestGoApiDiff(object):

    @pytest.fixture(autouse=True)
    def prepare(self, request):
        for f in request.funcargnames:
            if f.startswith('pair_'):
                pair = request.getfuncargvalue(f)
                break
        self.input_data = {}
        for i in range(2):
            pid = ProjectID.get(pair[i]['name'], pair[i]['commit'])
            api = os.path.join(configuration['testdatadir'], pid) + '-api.json'
            try:
                with open(api, 'rb') as f:
                    self.input_data['exported_api_{}'.format(i + 1)] = json.load(f)
            except IOError:
                raise RuntimeError(
                    'Cannot load exported API from file "{}"'.format(api))

    def test_identical_commits(self, pair_identical_commits):
        plugin = GoApiDiff()
        assert plugin.setData(self.input_data)
        assert plugin.execute()

    def test_different_projects(self, pair_different_projects):
        plugin = GoApiDiff()
        assert not plugin.setData(self.input_data)

    def test_generic(self, pair_generic):
        plugin = GoApiDiff()
        assert plugin.setData(self.input_data)
        assert plugin.execute()
