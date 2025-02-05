# diy templating.
# jinja was too much.
# std lib template couldnt do dots

class Variable:
    def __init__(self, name: str):
        self.name = name
    def __str__(self):
        return '${'+str(self.name)+'}'

class String:
    def __init__(self, s: str):
        self.value = s
        
    def substitue(self, subs: dict[Variable|str, str], MAX_SUBS=999) -> str:
        from itertools import cycle
        s = self.value
        for i, (n,v) in enumerate(cycle(subs.items())):
            if i>MAX_SUBS:
                from warnings import warn
                warn('reached substitition lim')
                return s
            if isinstance(n, str): n = Variable(n)
            else: assert(isinstance(n, Variable))
            _ = s.replace(str(n), str(v))
            if _ == s: break
            else: s = _
        return s

