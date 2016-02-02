RESOURCE_RPM = "rpm"
RESOURCE_USER_DIRECTORY = "user-directory"
RESOURCE_UPSTREAM_SOURCE_CODES = "upstream-source-code"

RESOURCE_TYPE_DIRECTORY = "directory"
RESOURCE_TYPE_RPM = "rpm"
RESOURCE_TYPE_TARBALL = "tarball"

SUBRESOURCE_DIRECTORY_TREE = "directory-tree"

RESOURCE_FIELD = "resource"

class ResourceNotFoundError(RuntimeError):
   def __init__(self, err):
      self.err = err

