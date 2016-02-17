import json
import logging
import os
import shutil
import sys
import tempfile

import git

from infra.system.tests.utils import ProjectID
from infra.system.plugins.gosymbolextractor.extractor import GoSymbolExtractor


CONFIG_FILE_NAME = 'testdata.json'


class TestDataFetcher(object):

    def __init__(self):
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(levelname)s: %(message)s')
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def _fetchProject(self, targetdir, clone_url, name, commits, skip_dirs):
        self.logger.info('Fetching project "{}"'.format(name))
        try:
            workdir = tempfile.mkdtemp()
        except IOError:
            self.logger.error('Cannot create temporary working directory')
            return
        try:
            try:
                repo = git.Repo.clone_from(clone_url, workdir)
            except git.exc.GitCommandError:
                self.logger.error(
                    'Cannot clone git repository "{}" to "{}"'.format(
                        clone_url, workdir))
                return
            for commit in commits:
                self.logger.info('Processing commit "{}"'.format(commit))
                pid = ProjectID.get(name, commit)
                archive = os.path.join(targetdir, pid) + '.tar.gz'
                prefix = os.path.join(commit, '')
                try:
                    with open(archive, 'wb') as f:
                        repo.archive(f, commit, prefix, format='tar.gz')
                except (IOError, git.exc.GitCommandError):
                    self.logger.error(
                        'Cannot create archive "{}"'.format(archive))
                    continue
                try:
                    repo.git.checkout(commit)
                except git.exc.GitCommandError:
                    self.logger.warn(
                        'Cannot checkout to commit "{}"'.format(commit))
                    continue
                input_data = {
                    'source_code_directory': workdir,
                    'directories_to_skip': skip_dirs,
                    'project': name,
                    'commit': commit,
                    'ipprefix': name,
                }
                try:
                    plugin = GoSymbolExtractor()
                    if not plugin.setData(input_data):
                        self.logger.warn('Failed to set input data to ' +
                            'GoSymbolExtractor plugin')
                        continue
                    if not plugin.execute():
                        self.logger.warn('Failed to execute ' +
                            'GoSymbolExtractor plugin')
                        continue
                    output_data = plugin.getData()
                    if not output_data:
                        self.logger.warn('Failed to get output data from ' +
                            'GoSymbolExtractor plugin')
                        continue
                except:
                    self.logger.warn('Unhandled exception occured during ' +
                        'execution of GoSymbolExtractor plugin')
                    continue
                api = os.path.join(targetdir, pid) + '-api.json'
                try:
                    with open(api, 'wb') as f:
                        json.dump(output_data[1], f)
                except IOError:
                    self.logger.error(
                        'Cannot save exported API to file "{}"'.format(api))
                    continue
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
        
    def fetch(self, targetdir, projects):
        for project in projects:
            self._fetchProject(
                targetdir, project['clone_url'], project['name'],
                project['commits'], project['skip_dirs'])


if __name__ == '__main__':
    fetcher = TestDataFetcher()
    path = os.path.dirname(os.path.realpath(__file__))
    configfile = os.path.join(path, CONFIG_FILE_NAME)
    try:
        with open(configfile, 'rb') as f:
            configuration = json.load(f)
    except IOError:
        fetcher.logger.error(
            'Cannot load configuration from "{}"'.format(configfile))
        sys.exit(1)
    if not os.path.isdir(configuration['testdatadir']):
        try:
            os.makedirs(configuration['testdatadir'])
        except OSError:
            fetcher.logger.error(
                'Cannot create target directory "{}"'.format(
                    configuration['testdatadir']))
            sys.exit(1)
    fetcher.fetch(configuration['testdatadir'], configuration['projects'])
