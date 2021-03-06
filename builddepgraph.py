# Dependency graph can be built in a various ways:
# - from the latest builds in Koji (for given distribution)
# - from a list of builds in Koji (for given distribution)
# - from a list of upstream commits
# - from a list of latest upstream commits
# - etc.
#
# In all cases I have to specify:
# - list of packages/projects to get dependencies from
# - list of builds/commits of each package/project
#
# TODO:
# - specify strategies (distro:latest, distro:selected, upstream:latest, upstream:selected)
#   - make an interface returning list of selected resources
# - retrieve data for all selected resources
# - from retrieved data select subset of all relevant data (list of provided packages, list of imported packages, etc.)
# - construct a dependency graph over the data (get a list of missing/unused packages)
# - detect distinctive patterns in the graph (cyclic dependencies, leafs, roots)
# 
# - define input schema for new plugin
# - define output schema for the plugin (constructed graph, missing/unused packages/ cyclic deps, leafs, roots)
#
# QUESTIONS:
# - Each graph is a printset for the current state of ecosystem, what else I need in the resulted artefact?
#   At the simplest case, it will be for defined packages only. It makes sense to extend the analysis to main
#   packages and unit-tests as well. Different views can provide different layers of a graph. One layer just for
#   devel subpackages, another for unit-tests and main packages. I can switch between them and combine them.
#   Find some tool for graph visualization.
# - Would be great to monitor the current state of builds (based on a date interval) so I can see how the
#   dependencies are changing over time (with each new build or periodically?)
#
#

from gofedlib.packagemanager import PackageManager
from gofedinfra.system.models.graphs.datasets.distributionlatestbuilds import DistributionLatestBuildGraphDataset
from gofedinfra.system.models.graphs.datasetdependencygraphbuilder import DatasetDependencyGraphBuilder
from gofedinfra.system.models.graphs.basicdependencyanalysis import BasicDependencyAnalysis
from gofedlib.graphutils import GraphUtils
from gofedinfra.system.models.graphs.datasets.projectdatasetbuilder import ProjectDatasetBuilder
from gofedinfra.system.models.graphs.datasets.localprojectdatasetbuilder import LocalProjectDatasetBuilder

import json
import logging
#logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
	# get a list of all packages
	packages = PackageManager().getPackages()

	#dataset = DistributionLatestBuildGraphDataset("rawhide", packages).build()
	#dataset = ProjectDatasetBuilder("github.com/coreos/etcd", "5e6eb7e19d6385adfabb1f1caea03e732f9348ad").build()
	dataset = LocalProjectDatasetBuilder("/home/jchaloup/Packages/etcd/fedora/etcd/etcd-5e6eb7e19d6385adfabb1f1caea03e732f9348ad", "github.com/coreos/etcd").build()

	graph = DatasetDependencyGraphBuilder().build(dataset, 2)
	#print str(graph)

	# get a subgraph
	#print str(GraphUtils.truncateGraph(graph, ["kubernetes-devel-1.2.0-0.15.alpha6.gitf0cd09a.fc25.noarch.rpm"]))

	print json.dumps(BasicDependencyAnalysis(graph).analyse().getResults())

	#DatasetBuilder("DistributionLatestBuild").\
	#	build("rawhide", packages).\
	#	graph(level)
	#DistributionLatestBuildGraphDataset("rawhide", packages).build().graph(level).build()



