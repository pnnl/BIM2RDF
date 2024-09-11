
current = 'current'
class Get:
    from pathlib import Path    
    def __init__(self,
            pth, *,
            rev=current,
            ) -> None:
        self.pth = self.Path(pth)
        self.rev = rev
    
    from functools import cached_property, cache
    @cached_property
    def fs(self):
        if self.rev == current:
            from fsspec.implementations.local import LocalFileSystem
            return LocalFileSystem()
        else:
            from dvc.api import DVCFileSystem
            return DVCFileSystem(rev=self.rev)
    
    @cache
    def read(self, mode='rb'):
        from dvc.api import DVCFileSystem
        if isinstance(self.fs, DVCFileSystem):
            fp = self.Path(__file__).parent.parent.parent.parent
            assert((fp / '.git').exists())
            fp = self.pth.resolve().absolute().relative_to(fp)
            fp = fp.as_posix()
            fp = '/'+str(fp)
        else:
            fp = self.pth
        return self.fs.open(fp, mode=mode).read()
    
    def __call__(self,):
        return self.read()
    
    
    def lines(self) -> '_.a|_.b':
        ext = self.pth.suffix[1:]
        if ext in txt_exts:
            _ = self()
            _ = _.decode()
            _ = _.splitlines()
        else: # treat as binary
            _ = self()
            from hashlib import md5
            _ = md5(_)
            _ = _.hexdigest()
            _ = [_]
        _ = [l+'\n' for l in _]
        return _


txt_exts = {'txt', 'yaml', 'yml', 'json',
                   'rq', 'ttl' }

class Diff:
    def __init__(self,
            gettera, getterb,
            context=3) -> None:
        self.ga = self.gettera = gettera
        self.gb = self.getterb = getterb
        self.context = context
    
    def __call__(self, *p, **k):
        from difflib import unified_diff as diff
        _ = diff(
            self.ga.lines(),
            self.gb.lines(),
            fromfile=str(self.ga.pth),
            tofile=  str(self.gb.pth),
            n=self.context)
        _ = ''.join(_)
        return _


from inspect import signature as sig
def diff(
        path_a, *,
        path_b=None,
         reva=sig(Get.__init__).parameters['rev'].default,
         revb=sig(Get.__init__).parameters['rev'].default,
         context=sig(Diff.__init__).parameters['context'].default,
         ):
    f"""
    if reva or revb is '{current}'
    it takes the content of the local (uncommitted) file
    """
    if path_b is None:
        path_b = path_a
    ga = Get(path_a, rev=reva)
    gb = Get(path_b, rev=revb)
    _ = Diff(ga, gb, context=context)
    _ = _()
    return _


if __name__ == '__main__':
    from fire import Fire
    print(
    Fire(diff)
    )

