#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

def getPackages():
	return ['gofedinfra',
		'gofedinfra.system.resources',
		'gofedinfra.system.models.ecomanagement.fetchers',
		'gofedinfra.system.models.ecomanagement.executors',
		'gofedinfra.system.models.ecomanagement.watchers',
		'gofedinfra.system.models.ecomanagement',
		'gofedinfra.system.models.ecomanagement.workers',
		'gofedinfra.system.models.ecosnapshots',
		'gofedinfra.system.models',
		'gofedinfra.system.models.snapshots',
		'gofedinfra.system.models.graphs.datasets',
		'gofedinfra.system.models.graphs',
		'gofedinfra.system.plugins.specdataextractor',
		'gofedinfra.system.plugins.goapidiff',
		'gofedinfra.system.plugins.goprojectcontentmetadataextractor',
		'gofedinfra.system.plugins.repositorydataextractor',
		'gofedinfra.system.plugins.simpleetcdstorage',
		'gofedinfra.system.plugins.simplefilestorage',
		'gofedinfra.system.plugins',
		'gofedinfra.system.plugins.distributionpackagebuildsextractor',
		'gofedinfra.system.plugins.gosymbolsextractor',
		'gofedinfra.system.plugins.distributiongosymbolsextractor',
		'gofedinfra.system.core.meta',
		'gofedinfra.system.core.factory',
		'gofedinfra.system.core.functions',
		'gofedinfra.system.core',
		'gofedinfra.system.core.acts',
		'gofedinfra.system',
		'gofedinfra.system.acts.scandistributionbuild',
		'gofedinfra.system.acts.scanupstreamrepository',
		'gofedinfra.system.acts.specmodeldataprovider',
		'gofedinfra.system.acts',
		'gofedinfra.system.acts.artefactwriter',
		'gofedinfra.system.acts.goexportedapidiff',
		'gofedinfra.system.acts.gocodeinspection',
		'gofedinfra.system.acts.scandistributionpackage',
		'gofedinfra.system.acts.artefactreader',
		'gofedinfra.system.config',
		'gofedinfra.system.artefacts',
		'gofedinfra.system.helpers.itemsetcache',
		'gofedinfra.system.helpers',
		'gofedinfra.system.helpers.artefactkeygenerator']

setup(
	name='gofedinfra',
	version='0.0.1',
	description='Gofed infrastructure',
	long_description=''.join(open('README.md').readlines()),
	keywords='gofed,infra',
	author='Jan Chaloupka',
	author_email='jchaloup@redhat.com',
	url='https://github.com/gofed/infra',
	license='GPL',
	packages=getPackages(),
	install_requires=open('requirements.txt').read().splitlines(),
	include_package_data=True
	#package_data={
	#	"gofedinfra.system.acts.artefactreader": ["gofedinfra/system/acts/artefactreader/*.json"]
	#},
	#package_dir={
	#	"gofedinfra.system.acts.artefactreader": "gofedinfra/system/acts/artefactreader/fakedata"
	#}
)
