import json

class_template = """
from system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class %s(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = "%s"):
		# return a list of fields
		keys = []
		for key in %s:
			if key not in data:
				logging.error("%s: %%s key missing" %% key)
				return ""

			keys.append(data[key])

		return delimiter.join(keys)
"""

def generateKeyClass(key_spec):
	obj = ClassGenerator(key_spec)

	if "delimiter" not in key_spec:
		delimiter = ":"
	else:
		delimiter = key_spec["delimiter"]

	return class_template % (obj.class_name(), delimiter, obj.class_keys(), key_spec["id"])

def generateKeyFF(key_spec):
	lines = []
	lines.append("from system.artefacts import artefacts")

	for key in key_spec:
		obj = ClassGenerator(key)
		lines.append("from %s import %s" % (obj.class_filename(), obj.class_name()))

	lines.append("\nclass KeyGeneratorFactory:\n")
	lines.append("\tdef build(self, artefact):\n")

	for key in key_spec:
		obj = ClassGenerator(key)

		lines.append("\t\tif artefact == artefacts.%s:" % key["artefact"])
		lines.append("\t\t\treturn %s()\n" % obj.class_name())

	lines.append("\t\traise ValueError(\"Invalid artefact: %s\" % artefact)")

	return "\n".join(lines)

if __name__ == "__main__":
	with open("artefacts.json", "r") as f:
		keys = json.load(f)

	# generate key generator
	with open("system/helpers/artefactkeygenerator/keygenerator.py", "w") as f:
		f.write(generateFF(keys))
	exit(1)

	for key in keys:
		class_def = generateClass(key)
		class_file_name = "%s.py" % key["id"].replace("-", "")
		with open(class_file_name, "w") as f:
			f.write(class_def)
			class_name = "%sKeyGenerator" % "".join(map(lambda i: i.capitalize(), key["id"].split("-")))
			print "class %s written into %s" % (class_name, class_file_name)
