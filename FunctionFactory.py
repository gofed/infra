from PureFunction import PureFunction

PF_ANALYSIS_API = 1
PF_ANALYSIS_DEPS = 2

def a(d):
	print "A: %s" % d

def b(d):
	print "B: %s" % d

class FunctionFactory:
	"""
	Factory baking pure functions

	https://github.com/gofed/infra/issues/10
	"""

	def __init__(self):
		self.recipes = {
			PF_ANALYSIS_API: a,
			PF_ANALYSIS_DEPS: b,
		}
		print "Factory ready to serve"

	def getInstance(self, pure_function_ID):
		if pure_function_ID not in self.recipes:
			return null

		fnc = self.recipes[pure_function_ID]
		return PureFunction(fnc)

if __name__ == "__main__":
	ff = FunctionFactory()
	f = ff.getInstance(PF_ANALYSIS_DEPS)

	f.call("Ahoj")
