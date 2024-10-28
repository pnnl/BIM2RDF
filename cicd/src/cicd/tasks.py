from inspect import signature as sig


def changed_files(*, patterns=['*'],  # parse like this exactly from cli
        v1='HEAD',
        v2='HEAD~1'):
    """lists changed files"""
    _ = f"git diff --name-only {v1} {v2}"
    from subprocess import check_output
    _ = check_output(_, text=True, shell=True)
    from pathlib import PurePath as Path
    _ = _.split('\n')
    _ = (p.strip() for p in _ if p)
    _ = map(Path, _)
    _ = (p for p in _ if any(p.match(ptrn) for ptrn in  patterns))
    _ = list(_)
    return _


def is_changed(*,
        patterns=sig(changed_files).parameters['patterns'].default,
        v1=     sig(changed_files).parameters['v1'].default,
        v2=     sig(changed_files).parameters['v2'].default,
        ):
    _ = changed_files(patterns=patterns, v1=v1, v2=v2)
    if _:
        return True
    else:
        return False


if __name__ == '__main__':
    from fire import Fire
    _ = {f.__name__:f for f in
         {
            is_changed,
            changed_files,
          } }
    Fire(_)
