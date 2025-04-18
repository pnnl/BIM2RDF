from tomllib import load
from pathlib import Path
pkgs = load(open(Path(__file__).parent / 'pyproject.toml', 'rb'))
pkgs = pkgs['tool']['uv']['workspace']['members']
pkgs.remove('project')
pkgs = [f"{pkgs[0]}-{p}" if i !=0 else p
      for i,p in enumerate(pkgs) ]
pkg = pkgs[0]


from subprocess import CalledProcessError
def get_rev():
    from subprocess import check_output as run
    return run('git rev-parse --abbrev-ref HEAD', text=True, shell=True).strip()
try:
    rev = get_rev()
except CalledProcessError: # no git in cicd maybe
    rev = '{NO GIT}' # 


def build(commit=False, packages=pkgs):
    def run(cmd, *p, **k):
        from subprocess import check_call as run
        from pathlib import Path
        return run(cmd, *p, cwd=Path(__file__).parent, shell=True, **k)
    if commit:  
        run(f'uvx hatchling version {ver(increment=True)}', )
        for pkg in packages: run(f'uv lock --upgrade-package {pkg}', ) 
        # https://github.com/pre-commit/pre-commit/issues/747#issuecomment-386782080
        run('git add -u', )

    run(f'uv build')
    return


def ver(*,increment=False):
    from datetime import datetime as dt
    dt = dt.now()
    mjr = str(dt.year)
    mnr = str(dt.month)
    pch = str(ncommits()+(1 if increment else 0))
    return f"{mjr}.{mnr}.{pch}"
def ncommits(rev=rev):
    from subprocess import check_output as run
    c = run(f'git rev-list --count {rev}', text=True).strip()
    return int(c)

def chk_ver():
    from bim2rdf import __version__ as v
    return str(v) == str(ver())


def test():
    from pathlib import Path
    tf = Path(__file__).parent / 'test' / 'test.py'
    assert(tf.exists())
    from test.test import all
    all()


if __name__ == '__main__':
    import bim2rdf # just to invoke patch in src/__init__.py
    from fire import Fire
    _ = {f.__name__:f for f in {build, chk_ver, test, ncommits, ver}}
    Fire(_)
