import json
import os

import pytest

from infra.system.plugins.specdataextractor.extractor import SpecDataExtractor
from infra.system.helpers.artefact_schema_validator import ArtefactSchemaValidator


CONFIG_FILE_NAME = 'specdataextractor.json'


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
        metafunc.parametrize('package', configuration['packages'])


class TestSpecDataExtractor(object):

    @pytest.fixture(autouse=True)
    def prepare(self, request, package):
        specfile = os.path.join(
            configuration['testdatadir'], package['specfile'])
        self.input_data = {
            'product': package['product'],
            'distribution': package['distribution'],
            'package': package['name'],
            'resource': specfile,
        }

    def test_valid_output(self, package):
        plugin = SpecDataExtractor()
        assert plugin.setData(self.input_data)
        assert plugin.execute()
        output_data = plugin.getData()
        validator = ArtefactSchemaValidator('golang-project-info-fedora')
        assert validator.validate(output_data[0])
        validator = ArtefactSchemaValidator('golang-project-to-package-name')
        assert validator.validate(output_data[1])
        validator = ArtefactSchemaValidator('golang-ipprefix-to-package-name')
        assert validator.validate(output_data[2])
