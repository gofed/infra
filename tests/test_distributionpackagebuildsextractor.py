import json
import os

import pytest

from infra.system.plugins.distributionpackagebuildsextractor.extractor import DistributionPackageBuildsExtractor
from infra.system.helpers.artefact_schema_validator import ArtefactSchemaValidator


CONFIG_FILE_NAME = 'distributionpackagebuildsextractor.json'


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
    if 'package' in metafunc.fixturenames:
        metafunc.parametrize('package', configuration['package'])


class TestDistributionPackagesBuildsExtractor(object):

    @pytest.fixture(autouse=True)
    def prepare(self, request, project):
        self.input_data = {
            'package': project['name'],
            'product': project['product'],
            'distribution': project['distribution']
        }

    def test_valid_output(self, project):
        plugin = DistributionPackageBuildsExtractor()
        assert plugin.setData(self.input_data)
        assert plugin.execute()
        output_data = plugin.getData()
        assert output_data
        for data in output_data:
            validator = ArtefactSchemaValidator(data['artefact'])
            assert validator.validate(data)
