from pathlib import Path
from typing import Literal

def env():
    from os import environ
    from .install import ShaclInstallation
    si = ShaclInstallation()
    return {**environ,
        'SHACL_HOME': str(si.home),
        'SHACL_CP': f"{si.lib}/*", # need a star for some reason
        'LOGGING': str(si.logging),
          }

def tryenv(k):
    # ugly
    try:
        return env()[k]
    except:
        return 'NOTSET'

def cmd(
        cmd:Literal['validate']|Literal['infer'],
        datafile: Path,
        shapesfile: Path=None,
        shacl_cp=tryenv('SHACL_CP'), jvm_args='', logging=tryenv('LOGGING'),
        ):
    """command passed to java to run topquadrant shacl"""
    if (shacl_cp == 'NOTSET') or (logging == 'NOTSET'):
        raise ValueError("shacl_cp or logging not set")

    assert(cmd in {'validate', 'infer'})
    logging = f"-Dlog4j.configurationFile={logging}" if logging else ''
    # class path
    # quote so no funny shell parsing happens (on linux)
    shacl_cp = f"-cp \"{shacl_cp}\"" 
    cmd = cmd[0].upper()+cmd[1:]
    cmd = f"java {jvm_args} {logging} {shacl_cp} org.topbraid.shacl.tools.{cmd}"
    _ = f"{cmd} -datafile {datafile} "
    if shapesfile:
        _ = _+f"-shapesfile {shapesfile}"
    return _


def check_proc_manually(cmd, proc):
    # further guard to fail
    # in case topquadrant does not exit with an error
    # that's why check is false below
    if any(w in proc.stderr.lower() for w in {'exception', 'error'}):
        from subprocess import CalledProcessError
        from sys import stderr
        print(proc.stderr, file=stderr)
        raise CalledProcessError(proc.returncode, cmd, stderr=proc.stderr)
    
    # filter out warnings to ensure valid ttl of stdout
    _ = []
    for l in proc.stdout.split('\n'):
        if ('warn' and 'riot') in l.lower():
            print(l)
        else:
            _.append(l)
    proc.stdout = ''.join(_)
    return proc

def validate(data: Path, shapes:Path=None):
    from subprocess import run
    c = cmd('validate', data, shapes)
    _ = run(
            c, check=False, env=env(), shell=True,
            capture_output=True, text=True )
    _ = check_proc_manually(c, _)
    return _

def infer(data: Path, shapes:Path=None):
    from subprocess import run
    c = cmd('infer', data, shapes)
    _ = run(
            c, check=False, env=env(), shell=True,
            capture_output=True, text=True )
    _ = check_proc_manually(c, _)
    return _


if __name__ == '__main__':
    from fire import Fire
    def printerrs(s):
        if (s.returncode != 0):
            print('ERRORS')
            print(s.stderr)
        return s.stdout
    def cinfer(data: Path, shapes:Path=None, out=Path('shacl-infer.ttl')):
        data = Path(data)
        shapes = Path(shapes)
        data = (data.as_posix())
        shapes = (shapes.as_posix())
        _ = infer(data, shapes)
        _ = printerrs(_)
        open(out, 'w').write(_)
        return out
    def cvalidate(data: Path, shapes:Path=None, out=Path('shacl-validate.ttl')):
        data = Path(data)
        shapes = Path(shapes)
        data = (data.as_posix())
        shapes = (shapes.as_posix())
        _ = validate(data, shapes)
        _ = printerrs(_)
        open(out, 'w').write(_)
        return out

    Fire({
        'cmd': cmd,
        'validate': cvalidate,
        'infer': cinfer
    })
