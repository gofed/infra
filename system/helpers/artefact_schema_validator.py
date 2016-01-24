from system.artefacts.artefacts import ARTEFACT_GOLANG_PROJECT_PACKAGES, ARTEFACT_GOLANG_PROJECT_EXPORTED_API
import logging
import os
import json
import jsonschema
from utils import getScriptDir
from schema_validator import SchemaValidator

SCHEMA_DIRECTORY="%s/../artefacts/schemas/" % (getScriptDir())

class ArtefactSchemaValidator:

	def __init__(self, artefact):
		self.artefact = artefact
		self.schema = "%s/%s.json" % (SCHEMA_DIRECTORY, artefact)

	def validate(self, json_data):
		validator = SchemaValidator()
		return validator.validateFromFile(self.schema, json_data)
