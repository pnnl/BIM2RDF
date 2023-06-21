from project import root
def run(cmd, cwd=root):
    from subprocess import run as _
    return _(cmd, cwd=cwd)

