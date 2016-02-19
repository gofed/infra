import json
import os
import shutil
import tarfile
import tempfile

import pytest

from infra.system.tests.utils import ProjectID
from infra.system.plugins.gosymbolextractor.extractor import GoSymbolsExtractor
from infra.system.helpers.artefact_schema_validator import ArtefactSchemaValidator


CONFIG_FILE_NAME = 'gosymbolsextractor.json'


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


@pytest.fixture(scope='module', autouse=True)
def initialize(request):
    try:
        configuration['workdir'] = tempfile.mkdtemp()
    except IOError:
        raise RuntimeError('Cannot create temporary working directory')
    def cleanup():
        shutil.rmtree(configuration['workdir'], ignore_errors=True)
    request.addfinalizer(cleanup)


class TestGoSymbolsExtractor(object):

    @pytest.fixture(autouse=True)
    def prepare(self, request, project):
        pid = ProjectID.get(project['name'], project['commit'])
        archive = os.path.join(configuration['testdatadir'], pid) + '.tar.gz'
        targetdir = os.path.join(configuration['workdir'], pid)
        try:
            with tarfile.open(archive, 'r:gz') as tar:
                tar.extractall(targetdir)
        except IOError:
            raise RuntimeError('Cannot open archive "{}"'.format(archive))
        except tarfile.TarError:
            raise RuntimeError('Cannot extract archive "{}"'.format(archive))
        self.input_data = {
            'resource': targetdir,
            'directories_to_skip': project['directories_to_skip'],
            'project': project['name'],
            'commit': project['commit'],
            'ipprefix': project['name'],
        }

    def test_valid_output(self, project):
        plugin = GoSymbolsExtractor()
        assert plugin.setData(self.input_data)
        assert plugin.execute()
        output_data = plugin.getData()
        assert output_data
        for data in output_data:
            validator = ArtefactSchemaValidator(data['artefact'])
            assert validator.validate(data)
