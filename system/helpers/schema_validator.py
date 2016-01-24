import jsonschema
import json
import logging

class SchemaValidator:

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
			jsonschema.validate(json_data, schema)
		except jsonschema.ValidationError, e:
			logging.error("Validation error: %s" % e)
			return False

		return True

