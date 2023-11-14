from pathlib import Path
from typing import Literal

def env():
    from os import environ
    from .install import ShaclInstallation
    si = ShaclInstallation()
    l = (si.home/'log4j2.properties')
    assert(l.exists())
    #l = str(l).replace("\\", "\\\\")
    assert(si.home.exists())
    assert(si.lib.exists())
    return {**environ,
        'SHACL_HOME': str(si.home),
        'SHACL_CP': f"{si.lib}/*", # need a star for some reason
        'LOGGING': str(l),
          }

def cmd(
        cmd:Literal['validate']|Literal['infer'],
        datafile: Path,
        shapesfile: Path=None,
        shacl_cp=env()['SHACL_CP'], jvm_args='', logging=env()['LOGGING'],
        ):
    assert(cmd in {'validate', 'infer'})
    cmd = cmd[0].upper()+cmd[1:]
    cmd = f"java {jvm_args} -Dlog4j.configurationFile={logging} -cp {shacl_cp} org.topbraid.shacl.tools.{cmd}"
    _ = f"{cmd} -datafile {datafile} "
    if shapesfile:
        _ = _+f"-shapesfile {shapesfile}"
    return _


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
    def cvalidate(data: Path, shapes:Path=None, out=Path('shacl-validate.ttl')):
        _ = validate(data, shapes)
        _ = printerrs(_)
        open(out, 'w').write(_)
        return out

    Fire({
        'validate': cvalidate,
        'infer': cinfer
    })
