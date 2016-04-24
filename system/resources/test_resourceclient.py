import unittest
from .client import ResourceClient
from .specifier import ResourceSpecifier
from .fakeresourcehandler import FakeResourceHandler
from .types import *
from infra.system.helpers.schema_validator import SchemaValidator
from gofed_lib.utils import getScriptDir
import os

class ResourceClientTest(unittest.TestCase):

	def test(self):

		c = ResourceClient(None, "")
		c._resource_handler = FakeResourceHandler(None, "")

		product = "Fedora"
		distribution = "f24"
		build = "gofed-0.0.10-3.fc24"
		rpm = "gofed-build-0.0.10-3.fc24.noarch.rpm"
		project = "fake-project"
		repository = {
			"provider": "github",
			"username": "fake",
			"project": "fake-project"
		}
		commit = "0000"
		provider = "github"
		username = "user"
		location = "fake/sub/resource/directory"

		specifications = [
			ResourceSpecifier().generateRpm(product, distribution, build, rpm),
			ResourceSpecifier().generateUserDirectory(location, type = RESOURCE_TYPE_DIRECTORY),
			ResourceSpecifier().generateUpstreamSourceCode(repository, commit),
			ResourceSpecifier().generateUpstreamRepository(repository)
		]

		schemas = {
			RESOURCE_RPM: "rpm_schema.json",
			RESOURCE_USER_DIRECTORY: "user_directory_schema.json",
			RESOURCE_UPSTREAM_SOURCE_CODES: "upstream_source_code_schema.json",
			RESOURCE_REPOSITORY: "upstream_repository_schema.json"
		}

		expected = {
			RESOURCE_RPM: "/fakeresourcehandler_ac811547d12c4b95b51633a24aea1950ac811547d12c4b95b51633a24aea1950",
			RESOURCE_USER_DIRECTORY: "fake/sub/resource/directory",
			RESOURCE_UPSTREAM_SOURCE_CODES: "/fakeresourcehandler_ac811547d12c4b95b51633a24aea1950ac811547d12c4b95b51633a24aea1950/rootdir",
			RESOURCE_REPOSITORY: "/fakeresourcehandler_ac811547d12c4b95b51633a24aea1950ac811547d12c4b95b51633a24aea1950/rootdir"
		}

		curr_dir = getScriptDir(__file__)
		validator = SchemaValidator()

		for s in specifications:
			# validate the schema
			schema = os.path.join(curr_dir, schemas[s["resource"]])
			self.assertTrue(validator.validateFromFile(schema, s))

			# retrieve subresource location
			self.assertEqual(c.retrieve(s).subresource(), expected[s["resource"]])

