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
        cmd('validate', data, shapes), env=env(), shell=True,
        capture_output=True, text=True )

def infer(data: Path, shapes:Path=None):
    from subprocess import run
    return run(
        cmd('infer', data, shapes), env=env(), shell=True,
        capture_output=True, text=True )


if __name__ == '__main__':
    from fire import Fire
    def printerrs(s):
        print(s.stderr)
        return s.stdout
    def cinfer(data: Path, shapes:Path=None, out=Path('shacl-infer.ttl')):
        _ = infer(data, shapes)
        _ = printerrs(_)
        open(out, 'w').write(_)
        return out
    def cvalidate(data: Path, shapes:Path=None, out=Path('shac-validate.ttl')):
        _ = validate(data, shapes)
        _ = printerrs(_)
        open(out, 'w').write(_)
        return out

    Fire({
        'validate': cvalidate,
        'infer': cinfer
    })
