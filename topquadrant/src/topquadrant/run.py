from pathlib import Path
from typing import Literal
def cmd(
        cmd:Literal['validate']|Literal['infer'],
        datafile: Path,
        shapesfile: Path=None):
    if cmd == 'validate':
        from .bin import validate
        cmd = validate
    else:
        assert(cmd == 'infer')
        from .bin import infer
        cmd = infer
    _ = f"{cmd} -datafile {datafile} "
    if shapesfile:
        _ = _+f"-shapesfile {shapesfile}"
    return _

    

def env():
    from os import environ
    from .install import ShaclInstallation
    si = ShaclInstallation()
    return {**environ,
        'SHACL_HOME': str(si.home),
        #'SHACL_CP': str(si.lib)
          }


def validate(data: Path, shapes:Path=None):
    from subprocess import run
    return run(
        cmd('validate', data, shapes), env=env(),
        capture_output=True, text=True )

def infer(data: Path, shapes:Path=None):
    from subprocess import run
    return run(
        cmd('infer', data, shapes), env=env(),
        capture_output=True, text=True )


