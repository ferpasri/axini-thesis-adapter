
# Module containing functionality to retrieve generated AML labels in
# domain specific format.

class Get:
  type: str = "get"
  interaction: str = "stimulus"
  form: str = "http"
  endpoint: str
  path: str
  headers: str
  
  def __init__(self, endpoint: str, path: str, headers: str):
    self.endpoint = endpoint
    self.path = path
    self.headers = headers

class Post:
  type: str = "post"
  interaction: str = "stimulus"
  form: str = "http"
  endpoint: str
  path: str
  headers: str
  body: str

  def __init__(self, endpoint: str, path: str, headers: str, body: str):
    self.endpoint = endpoint
    self.path = path
    self.headers = headers
    self.body = body

class Answer:
  type: str = "answer"
  interaction: str = "response"
  form: str = "http"
  code: int
  headers: str
  body: str
  
  def __init__(self, code: int, headers: str, body: str):
      self.code = code
      self.headers = headers
      self.body = body
      

class Labels:
  @staticmethod
  def labels():
    return [Labels.get(), Labels.post(), Labels.answer()]

  # Label that represents a generic 'GET' HTTP operation
  @staticmethod
  def get():
    return ('get', 'stimulus', 'http',
        {'endpoint': str, 'path': str, 'headers': str})

  # Label that represents a generic 'POST' HTTP operation
  @staticmethod
  def post():
    return ('post', 'stimulus', 'http',
        {'endpoint': str, 'path': str, 'body': str, 'headers': str})

  # Label that represents a generic answer to an HTTP operation
  @staticmethod
  def answer():
    return ('answer', 'response', 'http',
        {'code': int, 'headers': str, 'body': str})
