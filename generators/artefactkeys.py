import json
from .classhelper import ClassHelper

class_template = """from infra.system.core.meta.metaartefactkeygenerator import MetaArtefactKeyGenerator
import logging

class %sKeyGenerator(MetaArtefactKeyGenerator):

	def generate(self, data, delimiter = "%s"):
		# return a list of fields
		keys = []
		for key in %s:
			if key not in data:
				raise ValueError("%s: %%s key missing" %% key)
"""

class_template_extended = """
			keys.append(self.value2key(data[key], delimiter, key, %s))

		return delimiter.join(keys)
"""

class_template_end = """
			keys.append(self.truncateKey(data[key]))

		return delimiter.join(keys)
"""

def generateKeyClass(key_spec):
	obj = ClassHelper(key_spec)

	if "delimiter" not in key_spec:
		delimiter = ":"
	else:
		delimiter = key_spec["delimiter"]

	template = class_template % (obj.class_name(), delimiter, obj.class_keys(), key_spec["id"])
	if "key_order" in key_spec:
		template += class_template_extended % json.dumps(key_spec["key_order"])
	else:
		template += class_template_end

	return template

def generateKeyFF(key_spec):
	lines = []
	lines.append("from infra.system.artefacts import artefacts")

	for key in key_spec:
		obj = ClassHelper(key)
		lines.append("from .%s import %sKeyGenerator" % (obj.class_filename(), obj.class_name()))

	lines.append("\nclass KeyGeneratorFactory:\n")
	lines.append("\tdef build(self, artefact):\n")

	for key in key_spec:
		obj = ClassHelper(key)

		lines.append("\t\tif artefact == artefacts.%s:" % key["artefact"])
		lines.append("\t\t\treturn %sKeyGenerator()\n" % obj.class_name())

	lines.append("\t\traise ValueError(\"Invalid artefact: %s\" % artefact)")

	return "\n".join(lines)

if __name__ == "__main__":
	with open("generators/artefacts.json", "r") as f:
		keys = json.load(f)

	# generate key factory
	with open("system/helpers/artefactkeygenerator/keygenerator.py", "w") as f:
		f.write(generateKeyFF(keys))
		print("system/helpers/artefactkeygenerator/keygenerator.py")

	# generate artefact key generators
	for key in keys:
		obj = ClassHelper(key)
		class_def = generateKeyClass(key)
		with open("system/helpers/artefactkeygenerator/%s" % obj.class_filename_ext(), "w") as f:
			f.write(class_def)
			print("system/helpers/artefactkeygenerator/%s" % obj.class_filename_ext())
