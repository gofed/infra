import jsonschema
import json
import logging

class SchemaValidator:

	def __init__(self, base_directory = ""):
		self.base_directory = base_directory

	def validateFromFile(self, schema_file, json_data):
		schema = ""
		# get schema
		try:
			with open(schema_file, "r") as f:
				schema = json.loads(f.read())
 		except IOError, e:
			logging.error("Unable to load schema from %s" % schema_file)
			return False

		# validate
		try:
			if self.base_directory != "":
				resolver = jsonschema.RefResolver('file://' + self.base_directory + '/', schema)
				jsonschema.Draft4Validator(schema, resolver=resolver).validate(json_data)
			else:
				jsonschema.validate(json_data, schema)
		except jsonschema.ValidationError, e:
			logging.error("Validation error: %s" % e)
			return False

		return True

