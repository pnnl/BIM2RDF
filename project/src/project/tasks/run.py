from project import root
def run(cmd, cwd=root):
    if isinstance(cwd, str):
        cwd = root / cwd
    from subprocess import run as _
    return _(cmd, cwd=cwd, shell=True)

