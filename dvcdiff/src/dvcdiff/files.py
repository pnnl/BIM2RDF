
class Get:
    def __init__(self, pth, reva=None, revb=None) -> None:
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
            a = self.fs.a.open(self.pth, dvc_only=True)
            b = self.fs.a.open(self.pth, dvc_only=True)
        return _


class Diff:
    def __init__(self, getter) -> None:
        self.getter = getter
    

    def lines(self, a) -> list[str]:
        ...



def diff(a, b, reva=None, revb=None):
    g = Get(a, b, reva=None, revb=None)
    



if __name__ == '__main__':
    from fire import Fire
    Fire(diff)

