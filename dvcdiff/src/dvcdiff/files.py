from types import SimpleNamespace as NS

class Get:
    def __init__(self, pth, *, reva=None, revb=None) -> None:
        from pathlib import Path
        self.pth = Path(pth)
        self.reva = reva
        self.revb = revb
    
    from functools import cached_property
    @cached_property
    def fs(self):
        class _:
            from dvc.api import DVCFileSystem
            a = DVCFileSystem(rev=self.reva)
            b = DVCFileSystem(rev=self.revb)
        return _
    
    def __call__(self, ):
        class _:
            a = self.fs.a.open((self.pth.as_posix()))
            b = self.fs.b.open((self.pth.as_posix()))
        return _


class Diff:
    def __init__(self, getter) -> None:
        self.g = self.getter = getter
    
    def lines(self) -> '_.a|_.b':
        ext = self.g.pth.suffix[1:]
        g = self.getter()
        if ext in {'txt', 'yaml', 'yml', 'json'}:
            _ = NS(    
                a = g.a.read().decode().splitlines(),
                b = g.b.read().decode().splitlines())
            return _
        else: # treat as binary
            from hashlib import md5
            return NS(
                a = md5(g.a.read()).hexdigest(),
                b = md5(g.b.read()).hexdigest(),
            )
    
    def __call__(self, *p, **k):
        _ = self.lines()
        from difflib import unified_diff as diff
        _ = diff(
            [l+'\n' for l in _.a],
            [l+'\n' for l in _.b],
            fromfile=str(self.g.pth),
            tofile=  str(self.g.pth),
            n=3, lineterm='\n')
        _ = ''.join(_)
        return _


def diff(pth, *, reva=None, revb=None):
    g = Get(pth, reva=reva, revb=revb)
    _ = Diff(g)
    _ = _()
    return _



if __name__ == '__main__':
    from fire import Fire
    print(
    Fire(diff)
    )

