from infra.system.artefacts.artefacts import (
	ARTEFACT_GOLANG_PROJECT_PACKAGES,
	ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT
)
from gofedlib.go.importpath.decomposerbuilder import ImportPathsDecomposerBuilder
from gofedlib.go.importpath.normalizer import ImportPathNormalizer
from gofedlib.go.importpath.parserbuilder import ImportPathParserBuilder
from gofedlib.providers.providerbuilder import ProviderBuilder
from gofedlib.go.snapshot import Snapshot
import logging
import copy
import operator

from infra.system.models.graphs.datasets.projectdatasetbuilder import ProjectDatasetBuilder
from infra.system.models.graphs.datasetdependencygraphbuilder import DatasetDependencyGraphBuilder, LEVEL_GOLANG_PACKAGES
from gofedlib.graphs.graphutils import GraphUtils

from infra.system.workers import Worker
from infra.system.plugins.simplefilestorage.storagereader import StorageReader

class ReconstructionError(Exception):
	pass

class SnapshotReconstructor(object):

	def __init__(self):
		# parsers
		self.ipparser = ImportPathParserBuilder().buildWithLocalMapping()
		self._project_provider = ProviderBuilder().buildUpstreamWithLocalMapping()

		# snapshot
		self._snapshot = Snapshot()

		# dependency space
		self.detected_projects = {}
		self.unscanned_projects = {}
		self.scanned_projects = {}

	def _getCommitTimestamp(self, repository, commit):
		"""Retrieve commit from a repository, returns its commits date

		:param repository: repository
		:type  repository: dict
		:param commit: commit
		:type  commit: hex string
		"""
		artefact_key = {
			"artefact": ARTEFACT_GOLANG_PROJECT_REPOSITORY_COMMIT,
			"repository": self._project_provider.parse(repository).signature(),
			"commit": commit,
		}

		try:
			return StorageReader().retrieve(artefact_key)["cdate"]
		except KeyError:
			Worker("scanupstreamrepository").setPayload({
				"repository": repository,
				"hexsha": commit,
			}).do()
			return StorageReader().retrieve(artefact_key)["cdate"]

	def _findYoungestCommits(self, commits):
		# sort commits
		commits = map(lambda l: {"c": l, "d": commits[l]["cdate"]}, commits)
		commits = sorted(commits, key = lambda commit: commit["d"])

		return commits[-1]

	def _findClosestCommit(self, repository, timestamp):
		"""Get the oldest commits from the repository that is at most old as timestamp.

		:param repository: repository
		:type  repository: dict
		:param timestamp: commit timestamp
		:type  timestamp: integer
		"""
		# TODO(jchaloup): search for commits only on master branch!!!
		# other branches can be in inconsystem state with experimental features
		# and get picked unintensionaly
		data = {
			"repository": repository,
			"end_timestamp": timestamp
		}

		DAY = 3600*24
		# try the last day, week, last month, last year, all the time
		for delta in [DAY, 7*DAY, 30*DAY, 365*DAY, timestamp]:
			from_ts = timestamp - delta

			Worker("scanupstreamrepository").setPayload({
				"repository": repository,
				"from_ts": from_ts,
				"to_ts": timestamp,
			}).do()
			info_artefact = StorageReader().retrieve({
				"artefact": "golang-project-repository-info",
				"repository": self._project_provider.parse(repository).signature(),
			})

			# TODO(jchaloup): we should not iterate over all branches
			potential_commits = {}
			for branch in info_artefact["branches"]:
				for commit in branch["commits"]:
					if branch["commits"][commit] < from_ts:
						continue

					potential_commits[commit] = branch["commits"][commit]

			if potential_commits:
				sorted_commits = sorted(potential_commits.items(), key=operator.itemgetter(1))
				c, _ = sorted_commits[-1]
				return c

		raise KeyError("No closest commit found for {}".format(repository))

	def _detectNextDependencies(self, dependencies, ipprefix, commit_timestamp):
		dependencies = list(set(dependencies))
		# normalize paths
		normalizer = ImportPathNormalizer()
		dependencies = map(lambda l: normalizer.normalize(l), dependencies)

		decomposer = ImportPathsDecomposerBuilder().buildLocalDecomposer()
		decomposer.decompose(dependencies)
		prefix_classes = decomposer.classes()

		next_projects = {}

		for prefix in prefix_classes:
			# filter out Native prefix
			if prefix == "Native":
				continue

			# filter out project's import path prefix
			if prefix == ipprefix:
				continue

			logging.warning("Processing %s ..." % prefix)

			# for each imported path get a list of commits in a given interval
			try:
				self.ipparser.parse(prefix)
				# ipprefix already covered?
				if self.ipparser.prefix() in self.detected_projects:
					# ip covered in the prefix class?
					not_covered = []
					for ip in prefix_classes[prefix]:
						if ip not in self.detected_projects[prefix]:
							not_covered.append(ip)

					if not_covered == []:
						logging.warning("Prefix %s already covered" % prefix)
						continue

						logging.warning("Some paths '%s' not yet covered in '%s' prefix" % (str(not_covered), prefix))
					# scan only ips not yet covered
					prefix_classes[prefix] = not_covered

				# iprefix -> provider prefix
				project_provider = self._project_provider.parse(prefix)

				provider = project_provider.signature()
				provider_prefix = project_provider.prefix()
			except ValueError as e:
				raise ReconstructionError("Prefix provider error: %s" % e)

			try:
				closest_commit = self._findClosestCommit(provider_prefix, commit_timestamp)

			except KeyError as e:
				raise ReconstructionError("Closest commit to %s timestamp for %s not found" % (commit_timestamp, provider_prefix))

			# update packages to scan
			next_projects[prefix] = {
				"ipprefix": prefix,
				"paths": map(lambda l: str(l), prefix_classes[prefix]),
				"provider": provider,
				"commit": closest_commit,
				"provider_prefix": provider_prefix
			}

		return next_projects

	def _detectDirectDependencies(self, repository, commit, ipprefix, commit_timestamp, mains, tests):
		artefact_key = {
			"artefact": ARTEFACT_GOLANG_PROJECT_PACKAGES,
			"repository": self._project_provider.parse(repository).signature(),
			"commit": commit,
		}

		try:
			packages_artefact = StorageReader().retrieve(artefact_key)
		except KeyError:
			Worker("gocodeinspection").setPayload({
				"repository": repository,
				"commit": commit,
				"ipprefix": ipprefix,
			}).do()
			packages_artefact = StorageReader().retrieve(artefact_key)

		# collect dependencies
		direct_dependencies = []
		for package in packages_artefact["data"]["dependencies"]:
			direct_dependencies = direct_dependencies + map(lambda l: l["name"], package["dependencies"])

		if mains != []:
			paths = {}
			for path in packages_artefact["data"]["main"]:
				paths[path["filename"]] = path["dependencies"]

			for main in mains:
				if main not in paths:
					raise ReconstructionError("Main package file %s not found" % main)

				direct_dependencies = direct_dependencies + paths[main]

		if tests:
			for dependencies in map(lambda l: l["dependencies"], packages_artefact["data"]["tests"]):
				direct_dependencies = direct_dependencies + dependencies

		# remove duplicates
		direct_dependencies = list(set(direct_dependencies))

		next_projects = self._detectNextDependencies(direct_dependencies, ipprefix, commit_timestamp)

		# update detected projects
		for project in next_projects:
			self.detected_projects[project] = next_projects[project]["paths"]

		# update packages to scan
		for prefix in next_projects:
			if prefix in self.unscanned_projects:
				continue

			self.unscanned_projects[prefix] = copy.deepcopy(next_projects[prefix])
			self.scanned_projects[prefix] = copy.deepcopy(next_projects[prefix])

	def _detectIndirectDependencies(self, ipprefix, commit_timestamp):
		nodes = []
		next_projects = {}
		for prefix in self.unscanned_projects:
			# get dataset
			dataset = ProjectDatasetBuilder(
				self.unscanned_projects[prefix]["provider_prefix"],
				self.unscanned_projects[prefix]["commit"],
				self.unscanned_projects[prefix]["ipprefix"]
			).build()

			# construct dependency graph from the dataset
			graph = DatasetDependencyGraphBuilder().build(dataset, LEVEL_GOLANG_PACKAGES)

			# get the subgraph of evolved dependency's packages
			subgraph = GraphUtils.truncateGraph(graph, self.unscanned_projects[prefix]["paths"])

			# get dependencies from the subgraph
			package_nodes = filter(lambda l: l.startswith(self.unscanned_projects[prefix]["ipprefix"]), subgraph.nodes())
			label_edges = dataset.getLabelEdges()
			for node in package_nodes:
                                # package that does not import any other package has no edge -> the label_edges[node] does not exist then
                                if node in label_edges:
                                        nodes = nodes + label_edges[node]

		nodes = list(set(nodes))

		next_projects = self._detectNextDependencies(nodes, ipprefix, commit_timestamp)
		if next_projects == {}:
			return False

		# update packages to scan
		one_at_least = False
		self.unscanned_projects = {}

		for prefix in next_projects:
			# prefix already covered? Just extend the current coverage
			if prefix in self.detected_projects:
				for ip in next_projects[prefix]["paths"]:
					if str(ip) not in self.detected_projects[prefix]:
						self.detected_projects[prefix].append(ip)
						self.scanned_projects[prefix]["paths"].append(ip)
				continue

			one_at_least = True
			self.unscanned_projects[prefix] = copy.deepcopy(next_projects[prefix])
			self.scanned_projects[prefix] = copy.deepcopy(next_projects[prefix])
			self.detected_projects[prefix] = copy.deepcopy(next_projects[prefix]["paths"])

		return one_at_least

	def reconstruct(self, repository, commit, ipprefix, mains = [], tests = False):
		"""Reconstruct snapshot
		:param repository: project repository
		:type  repository: dict
		:param commit: repository commit
		:type  commit: string
		:param ipprefix: import path prefix
		:type  ipprefix: string
		:param mains: list of main packages with root path to go file to cover, implicitly no main package, just devel
		:type  mains: [string]
		:param tests: cover unit tests as well, default is False
		:type  tests: boolean
		"""

		# clear snapshot
		self._snapshot.clear()

		# get commit date of project's commit
		commit_timestamp = self._getCommitTimestamp(repository, commit)
		# get direct dependencies
		logging.info("=============DIRECT==============")
		self._detectDirectDependencies(repository, commit, ipprefix, commit_timestamp, mains, tests)

		# scan detected dependencies
		logging.info("=============UNDIRECT==============")
		while self._detectIndirectDependencies(ipprefix, commit_timestamp):
			logging.info("=============UNDIRECT==============")

		# create snapshot
		for prefix in self.scanned_projects:
			for ip in sorted(self.scanned_projects[prefix]["paths"]):
				self._snapshot.addPackage(ip, self.scanned_projects[prefix]["commit"])

		return self

	def snapshot(self):
		return self._snapshot
