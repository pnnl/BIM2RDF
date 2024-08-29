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
    

    def lines(self) -> list[str]:
        ext = self.g.pth.suffix[1:]
        if ext in {'txt', 'yaml', 'yml', 'json'}:
            _ = self.g()
            _ = NS(    
                a = _.a.read().decode().splitlines(),
                b = _.b.read().decode().splitlines())
            return _
    
    def __call__(self, *p, **k):
        _ = self.lines()
        from difflib import diff
        _ = diff(
            _.a, _.b,
            fromfile=self.g.a, tofile=self.g.b,
            n=3, lineterm='\n')
        return _


def diff(pth, *, reva=None, revb=None):
    g = Get(a, b, reva=None, revb=None)
    return Diff(g)()



if __name__ == '__main__':
    from fire import Fire
    Fire(diff)

