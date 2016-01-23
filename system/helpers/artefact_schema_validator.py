import logging
import os
import json
import jsonschema
from utils import getScriptDir

SCHEMA_DIRECTORY="%s/../artefacts/schemas/" % (getScriptDir())

ARTEFACT_GOLANG_PROJECT_PACKAGES = "golang-project-packages"
ARTEFACT_GOLANG_PROJECT_EXPORTED_API = "golang-project-exported-api"

class ArtefactSchemaValidator:

	def __init__(self, artefact):
		self.artefact = artefact
		self.schema = "%s/%s.json" % (SCHEMA_DIRECTORY, artefact)

	def validate(self, json_data):
		schema = ""
		# get schema
		try:
			with open(self.schema, "r") as f:
				schema = json.loads(f.read())
 		except IOError, e:
			logging.error("Unable to load schema for %s artefact" % artefact)
			return False

		# validate
		try:
			jsonschema.validate(json_data, schema)
		except jsonschema.ValidationError, e:
			logging.error("Validation error: %s" % e)
			return False

		return True

