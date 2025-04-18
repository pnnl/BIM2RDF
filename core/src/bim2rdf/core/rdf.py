def _():
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

    from dataclasses import dataclass
    @dataclass(frozen=True)
    class Prefix:
        name:   str
        uri:    URI   # field(converter=URI) need attrs or pydantic??
                      # hackery below to avoid installing attrs or pydantic
    return URI, Prefix
from types import SimpleNamespace
_ = _()
locals()['types'] = SimpleNamespace(URI=_[0], Prefix=_[1])

# constructors
def Prefix(name: str, prefix: types.URI) -> types.Prefix:
    return types.Prefix(
        name=name,
        uri=types.URI(prefix))

def URI(u: str) -> types.URI:
    return types.URI(u)
