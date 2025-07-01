class URI(str):
    def __init__(self, s):
        _ = self.parse(s)
        assert(_.scheme)
        #assert(_.path)
        self._s = s
        super().__init__()
    
    def __repr__(self):
        return f"{self.__class__.__name__}({self._s})"
    
    @property
    def parts(self): return self.parse(self._s)

    @staticmethod
    def parse(s: str):
        from urllib.parse import urlparse
        _ = urlparse(s)
        return _


class Prefix:
    def __init__(self, name, uri) -> None:
        self.name = name
        self.uri = uri

    @property
    def name(self) -> str:
        return self._name
    @name.setter
    def name(self, v):
        self._name = str(v)
    
    @property
    def uri(self) -> URI:
        return self._uri
    @uri.setter
    def uri(self, v):
        _ = str(v)
        _ = _.strip().strip('<').strip('>')
        self._uri = URI(_)


