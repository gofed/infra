import json
import os

import pytest

from infra.system.plugins.distributionbuildextractor.extractor import DistributionBuildExtractor
from infra.system.helpers.artefact_schema_validator import ArtefactSchemaValidator


CONFIG_FILE_NAME = 'distributionbuildextractor.json'


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
    if 'project' in metafunc.fixturenames:
        metafunc.parametrize('project', configuration['projects'])


class TestRepositoryDataExtractor(object):

    @pytest.fixture(autouse=True)
    def prepare(self, request, project):
        self.input_data = {
            'project': project['name'],
            'product': project['product'],
            'distribution': project['distribution'],
            'repository': project['repository'],
            'clone_url': project['repository'],
        }

    def test_valid_output(self, project):
        plugin = DistributionBuildExtractor()
        assert plugin.setData(self.input_data)
        assert plugin.execute()
        output_data = plugin.getData()
        assert output_data
        for data in output_data:
            validator = ArtefactSchemaValidator(data['artefact'])
            assert validator.validate(data)
