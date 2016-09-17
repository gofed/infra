import json
from .classhelper import ClassHelper

def generateEtcdStorageArtefactFactory(key_spec):
	lines = []
	lines.append("from infra.system.artefacts import artefacts")
	lines.append("from .artefactdriver import ArtefactDriver")
	lines.append("\nclass ArtefactDriverFactory(object):\n")
	lines.append("\tdef __init__(self):")
	lines.append("\t\tself.artefacts = []\n")

	for key in key_spec:
		lines.append("\t\tself.artefacts.append(artefacts.%s)" % key["artefact"])

	lines.append("")
	lines.append("\tdef build(self, artefact):")
	lines.append("\t\tif artefact not in self.artefacts:")
	lines.append("\t\t\traise KeyError(\"Artefact '%s' not supported\" % artefact)\n")
	lines.append("\t\treturn ArtefactDriver(artefact)")

	return "\n".join(lines)

def generateFileStorageArtefactFactory(key_spec):
	lines = []
	lines.append("from infra.system.artefacts import artefacts")
	lines.append("from .artefactdriver import ArtefactDriver")
	lines.append("from infra.system.config.config import InfraConfig")
	lines.append("\nclass ArtefactDriverFactory(object):\n")
	lines.append("\tdef __init__(self):")
	lines.append("\t\tself.working_directory = InfraConfig().simpleFileStorageWorkingDirectory()")
	lines.append("\t\tself.artefacts = []\n")

	for key in key_spec:
		lines.append("\t\tself.artefacts.append(artefacts.%s)" % key["artefact"])

	lines.append("")
	lines.append("\tdef build(self, artefact):")
	lines.append("\t\tif artefact not in self.artefacts:")
	lines.append("\t\t\traise KeyError(\"Artefact '%s' not supported\" % artefact)\n")
	lines.append("\t\treturn ArtefactDriver(self.working_directory, artefact)")

	return "\n".join(lines)

if __name__ == "__main__":
	with open("generators/artefacts.json", "r") as f:
		keys = json.load(f)

	# generate file storage artefact driver factory
	with open("gofedinfra/system/plugins/simplefilestorage/artefactdriverfactory.py", "w") as f:
		f.write(generateFileStorageArtefactFactory(keys))
		print("gofedinfra/system/plugins/simplefilestorage/artefactdriverfactory.py")

	# generate driver factory
	with open("gofedinfra/system/plugins/simpleetcdstorage/artefactdriverfactory.py", "w") as f:
		f.write(generateEtcdStorageArtefactFactory(keys))
		print("gofedinfra/system/plugins/simpleetcdstorage/artefactdriverfactory.py")

