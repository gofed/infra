#
# As default, reconstructoror will construct the snapshot for a devel part of a project.
# 
#
# TODO(jchaloup):
# - fill and return snapshot
# - move snapshot data type into gofed/lib

from infra.system.core.factory.actfactory import ActFactory
from infra.system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES
from gofed_lib.importpathsdecomposerbuilder import ImportPathsDecomposerBuilder
from gofed_lib.importpathnormalizer import ImportPathNormalizer
from gofed_lib.importpathparserbuilder import ImportPathParserBuilder
from .snapshot import Snapshot
import logging

from infra.system.models.graphs.datasets.projectdatasetbuilder import ProjectDatasetBuilder
from infra.system.models.graphs.datasetdependencygraphbuilder import DatasetDependencyGraphBuilder, LEVEL_GOLANG_PACKAGES
from gofed_lib.graphutils import GraphUtils

class ReconstructionError(Exception):
	pass

class SnapshotReconstructor(object):

	def __init__(self):
		# parsers
		self.ipparser = ImportPathParserBuilder().buildWithLocalMapping()

		# acts
		self.go_code_inspection_act = ActFactory().bake("go-code-inspection")
		self.scan_upstream_repository_act = ActFactory().bake("scan-upstream-repository")

		# snapshot
		self.snapshot = Snapshot()

		# dependency space
		self.detected_projects = {}
		self.unscanned_projects = {}

	def _getCommitTimestamp(self, repository, commit):
		"""Retrieve commit from a repository, returns its commits date

		:param repository: repository
		:type  repository: dict
		:param commit: commit
		:type  commit: hex string
		"""
		data = {
			"repository": repository,
			"commit": commit
		}
		# TODO(jchaloup): catch exception if the commit is not found
		commit_data = self.scan_upstream_repository_act.call(data)
		return commit_data["commits"][commit]["cdate"]

	def _findYoungestCommits(self, commits):
		# sort commits
		commits = map(lambda l: {"c": l, "d": commits[l]["cdate"]}, commits)
		commits = sorted(commits, key = lambda commit: commit["d"])

		return commits[-1]

	def findClosestCommit(self, repository, timestamp):
		"""Get the oldest commits from the repository that is at most old as timestamp.

		:param repository: repository
		:type  repository: dict
		:param timestamp: commit timestamp
		:type  timestamp: integer
		"""
		data = {
			"repository": repository,
			"end_timestamp": timestamp
		}

		DAY = 3600*24
		# try the last day, week, last month, last year
		for delta in [1, 7, 30, 365]:
			data["start_timestamp"] = timestamp - delta*DAY
			rdata = self.scan_upstream_repository_act.call(data)
			if rdata["commits"] != {}:
				return self._findYoungestCommits(rdata["commits"])

		# unbound start_timestamp
		del data["start_timestamp"]
		rdata = self.scan_upstream_repository_act.call(data)
		if rdata["commits"] != {}:
			return self._findYoungestCommits(rdata["commits"])

		# no commit foud => raise exception
		raise KeyError("Commit not found")

	def detectNextDependencies(self, dependencies, ipprefix, commit_timestamp):
		dependencies = list(set(dependencies))
		# normalize paths
		normalizer = ImportPathNormalizer()
		dependencies = map(lambda l: normalizer.normalize(l), dependencies)

		decomposer = ImportPathsDecomposerBuilder().buildLocalDecomposer()
		decomposer.decompose(dependencies)
		prefix_classes = decomposer.getClasses()

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
				if self.ipparser.getImportPathPrefix() in self.detected_projects:
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

				provider = self.ipparser.getProviderSignature()
				provider_prefix = self.ipparser.getProviderPrefix()
			except ValueError as e:
				raise ReconstructionError("Prefix provider error: %s" % e)

			try:
				closest_commit = self.findClosestCommit(provider, commit_timestamp)
			except KeyError as e:
				raise ReconstructionError("Closest commit to %s timestamp for %s not found" % (commit_timestamp, provider_prefix))

			# save all imported packages
			for package in prefix_classes[prefix]:
				self.snapshot.addPackage(package, closest_commit["c"])

			# update packages to scan
			next_projects[prefix] = {
				"ipprefix": prefix,
				"paths": prefix_classes[prefix],
				"provider": provider,
				"commit": closest_commit["c"],
				#"timestamp": closest_commit["d"],
				"provider_prefix": provider_prefix
			}

		return next_projects

	def detectDirectDependencies(self, repository, commit, ipprefix, commit_timestamp):
		data = {
			"type": "upstream_source_code",
			"project": "github.com/coreos/etcd",
			"commit": commit,
			"ipprefix": ipprefix,
			"directories_to_skip": []
		}

		packages_artefact = self.go_code_inspection_act.call(data)

		# collect dependencies
		direct_dependencies = []
		for package in packages_artefact["data"]["dependencies"]:
			direct_dependencies = direct_dependencies + map(lambda l: l["name"], package["dependencies"])

		next_projects = self.detectNextDependencies(direct_dependencies, ipprefix, commit_timestamp)

		# update detected projects
		for project in next_projects:
			self.detected_projects[project] = next_projects[project]["paths"]

		# update packages to scan
		for prefix in next_projects:
			if prefix in self.unscanned_projects:
				continue

			self.unscanned_projects[prefix] = next_projects[prefix]

	def detectIndirectDependencies(self, ipprefix, commit_timestamp):
		nodes = []
		next_projects = {}
		for prefix in self.unscanned_projects:
			# get dataset
			dataset = ProjectDatasetBuilder(
				self.unscanned_projects[prefix]["provider_prefix"],
				self.unscanned_projects[prefix]["commit"]
			).build()

			# construct dependency graph from the dataset
			graph = DatasetDependencyGraphBuilder().build(dataset, LEVEL_GOLANG_PACKAGES)

			# get the subgraph of evolved dependency's packages
			subgraph = GraphUtils.truncateGraph(graph, self.unscanned_projects[prefix]["paths"])

			# get dependencies from the subgraph
			package_nodes = filter(lambda l: l.startswith(self.unscanned_projects[prefix]["ipprefix"]), subgraph.nodes())
			label_edges = dataset.getLabelEdges()
			for node in package_nodes:
				nodes = nodes + label_edges[node]

		nodes = list(set(nodes))

		next_projects = self.detectNextDependencies(nodes, ipprefix, commit_timestamp)
		if next_projects == {}:
			return False

		# update packages to scan
		one_at_least = False
		self.unscanned_projects = {}

		for prefix in next_projects:
			# prefix already covered? Just extend the current coverage
			if prefix in self.detected_projects:
				for ip in next_projects[prefix]["paths"]:
					if ip not in self.detected_projects[prefix]:
						self.detected_projects[prefix].append(ip)
				continue

			one_at_least = True
			self.unscanned_projects[prefix] = next_projects[prefix]
			self.detected_projects[prefix] = next_projects[prefix]["paths"]

		return one_at_least

	def reconstruct(self, repository, commit, ipprefix):
		# get commit date of project's commit
		commit_timestamp = self._getCommitTimestamp(repository, commit)
		# get direct dependencies
		print "=============DIRECT=============="
		self.detectDirectDependencies(repository, commit, ipprefix, commit_timestamp)

		# scan detected dependencies
		print "=============UNDIRECT=============="
		while self.detectIndirectDependencies(ipprefix, commit_timestamp):
			print "=============UNDIRECT=============="

		exit(1)
