class DirectJSONComparator:

	def equal(self, json1, json2):
		# the same keys
		keys1 = set(json1.keys())
		keys2 = set(json2.keys())

		left_diff = list(keys1 - keys2)
		right_diff = list(keys2 - keys1)

		if left_diff != [] or right_diff != []:
			return False

		for key in json1.keys():
			if json1[key] != json2[key]:
				return False

		return True
