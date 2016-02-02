class FunctionNotFoundError(RuntimeError):
   def __init__(self, err):
      self.err = err

class FunctionFailedError(RuntimeError):
   def __init__(self, err):
      self.err = err
