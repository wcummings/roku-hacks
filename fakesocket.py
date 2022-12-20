# https://stackoverflow.com/questions/24728088/python-parse-http-response-string/24729316#24729316
from io import BytesIO

class FakeSocket():
    def __init__(self, response_bytes):
        self._file = BytesIO(response_bytes)
    def makefile(self, *args, **kwargs):
        return self._file