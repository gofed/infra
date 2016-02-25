from .utils import getScriptDir
from .schema_validator import SchemaValidator

SCHEMA_DIRECTORY="%s/../artefacts/schemas/" % (getScriptDir())

class ArtefactSchemaValidator:

	def __init__(self, artefact):
		self.artefact = artefact
		self.schema = "%s/%s.json" % (SCHEMA_DIRECTORY, artefact)

	def validate(self, json_data):
		validator = SchemaValidator()
		return validator.validateFromFile(self.schema, json_data)
