import json

if __name__ == "__main__":
	with open("generators/artefacts.json", "r") as f:
		keys = json.load(f)

	definitions = {}
	for artefact in keys:
		properties = {}
		for key in artefact["keys"]:
			if key == "artefact":
				properties[key] = {
					"type": "string",
					"description": "key part",
					"oneOf": [ { "enum": [artefact["id"] ] } ]
				}
				continue

			if "key_order" not in artefact or key not in artefact["key_order"]:
				properties[key] = {
					"type": "string",
					"description": "key part",
					"minlength": 1
				}
			else:
				subproperties = {}
				for subkey in artefact["key_order"][key]:
					subproperties[subkey] = {
						"type": "string",
						"description": "subkey part",
						"minLength": 1
					}

				properties[key] = {
					"type": "object",
					"description": "key part",
					"properties": subproperties,
					"required": artefact["key_order"][key]
				}

		definitions[ artefact["id"] ] = {
			"type": "object",
			"description": "artefact key",
			"properties": properties,
			"required": artefact["keys"]
		}

	anyOf = []
	for definition in sorted(definitions.keys()):
		anyOf.append({
			"$ref": "#/definitions/%s" % definition
		})

	schema = {
		"$schema": "http://json-schema.org/draft-04/schema#",
		"title": "Artefact reader act",
		"description": "Definition of act providing artefact data (auto-generated)",
		"anyOf": anyOf,
		"definitions": definitions
	}

	print json.dumps(schema, indent = 4)
