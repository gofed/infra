import sys

if __name__ == "gofedinfra":
	sys.modules['infra'] = sys.modules[__name__]
