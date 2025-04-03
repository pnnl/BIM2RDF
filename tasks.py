pkgs = [
    'bim2rdf',  # 'main'
    'mapping',  # -> bim2rdf-mapping. this is how it's named in its pyproject.toml
    'rules',    # ...
    'speckle',
    'spklauto',]
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


def build(commit=False):
    def run(cmd, *p, **k):
        from subprocess import check_call as run
        from pathlib import Path
        return run(cmd, *p, cwd=Path(__file__).parent, shell=True, **k)
    if commit:
        run(f'uvx hatchling version {ncommits()+1}', )
        run(f'uv lock --upgrade-package {pkg}', )
        # https://github.com/pre-commit/pre-commit/issues/747#issuecomment-386782080
        run('git add -u', )
    run('uv build', )


def ncommits(rev=rev):
    from subprocess import check_output as run
    c = run(f'git rev-list --count {rev}', text=True).strip()
    return int(c)


def chk_ver(rev=rev):
    from pytqshacl import __version__ as v
    assert(pkg) in locals()
    return str(v) == str(ncommits(rev=rev))


def test():
    from pathlib import Path
    tf = Path(__file__).parent / 'test' / 'test.py'
    assert(tf.exists())
    from test.test import all
    all()


if __name__ == '__main__':
    from fire import Fire
    _ = {f.__name__:f for f in {build, chk_ver, test}}
    Fire(_)