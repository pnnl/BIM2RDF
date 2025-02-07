# diy templating.
# jinja was too much.
# std lib template couldnt do dots

class Variable:
    def __init__(self, name: str):
        self.name = name
    def __str__(self):
        return '${'+str(self.name)+'}'

class String:
    def __init__(self, s: str, *,
                 substitutions: dict[Variable|str, str]={},
                 MAX_SUBS=999):
        self.value = s
        _ = {}
        for var,val in substitutions.items():
            if isinstance(var, str): var = Variable(var)
            else: assert(isinstance(var, Variable))
            _[var] = val
        self.substitions = _
        self.MAX_SUBS = MAX_SUBS
    
    def onepass(self):
        s = self.value
        for var,val in self.substitions.items():
            _ = s.replace(str(var), str(val))
            if s != _: yield _
            s = _

    from functools import cache
    @cache
    def __str__(self):
        return self.substitute()
    def substitute(self):
        for _ in self: pass
        return _
        
    def __iter__(self):
        i = 0
        s = self.value
        for _p in range(99999):
            for s in self.onepass():
                if i>=self.MAX_SUBS:
                    from warnings import warn
                    warn(f'reached substitition limit of {self.MAX_SUBS}')
                    yield s
                i += 1
            if self.value == s:
                yield s
                return
            self = self.__class__(s, substitutions=self.substitions)
        raise Exception('substutution state should not be here')
