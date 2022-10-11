import json
import os
import shutil
import tarfile
import tempfile

import pytest

from gofedinfra.system.tests.utils import ProjectID
from gofedinfra.system.plugins.repositorydataextractor.extractor import RepositoryDataExtractor
from gofedinfra.system.helpers.artefact_schema_validator import ArtefactSchemaValidator


CONFIG_FILE_NAME = 'repositorydataextractor.json'


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
    if 'repository' in metafunc.fixturenames:
        metafunc.parametrize('repository', configuration['repositories'])


@pytest.fixture(scope='module', autouse=True)
def initialize(request):
    try:
        configuration['workdir'] = tempfile.mkdtemp()
    except IOError:
        raise RuntimeError('Cannot create temporary working directory')
    def cleanup():
        shutil.rmtree(configuration['workdir'], ignore_errors=True)
    request.addfinalizer(cleanup)


class TestRepositoryDataExtractor(object):

    @pytest.fixture(autouse=True)
    def prepare(self, request, repository):
        project = '{provider}.com/{username}/{project}'.format(**repository)
        pid = ProjectID.get(project, 'repository')
        archive = os.path.join(configuration['testdatadir'], pid) + '.tar.gz'
        targetdir = os.path.join(configuration['workdir'], pid)
        try:
            with tarfile.open(archive, 'r:gz') as tar:
                def is_within_directory(directory, target):
                    
                    abs_directory = os.path.abspath(directory)
                    abs_target = os.path.abspath(target)
                
                    prefix = os.path.commonprefix([abs_directory, abs_target])
                    
                    return prefix == abs_directory
                
                def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
                
                    for member in tar.getmembers():
                        member_path = os.path.join(path, member.name)
                        if not is_within_directory(path, member_path):
                            raise Exception("Attempted Path Traversal in Tar File")
                
                    tar.extractall(path, members, numeric_owner=numeric_owner) 
                    
                
                safe_extract(tar, targetdir)
        except IOError:
            raise RuntimeError('Cannot open archive "{}"'.format(archive))
        except tarfile.TarError:
            raise RuntimeError('Cannot extract archive "{}"'.format(archive))
        self.input_data = {
            'repository': {
                'provider': repository['provider'],
                'username': repository['username'],
                'project': repository['project'],
            },
            'resource': targetdir,
            'commit': repository['commit'],
        }

    def test_valid_output(self, repository):
        plugin = RepositoryDataExtractor()
        assert plugin.setData(self.input_data)
        assert plugin.execute()
        output_data = plugin.getData()
        assert output_data
        validator = ArtefactSchemaValidator(output_data['artefact'])
        assert validator.validate(output_data)
