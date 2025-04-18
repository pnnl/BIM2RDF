import fire
### patch for dev env until new release
# https://github.com/google/python-fire/issues/589
import fire.inspectutils as fi
def _(component):
    try:
        from IPython.core import oinspect  # pylint: disable=import-outside-toplevel,g-import-not-at-top
        try:
            inspector = oinspect.Inspector(theme_name="Neutral")
        except TypeError:  # Only recent versions of IPython support theme_name.
            inspector = oinspect.Inspector()
        info = inspector.info(component)
        # IPython's oinspect.Inspector.info may return '<no docstring>'
        if info['docstring'] == '<no docstring>':
            info['docstring'] = None
    except ImportError:
        info = fi._InfoBackup(component)
    try:
        import inspect
        unused_code, lineindex = inspect.findsource(component)
        info['line'] = lineindex + 1
    except (TypeError, OSError):
        info['line'] = None
    if 'docstring' in info:
        from fire import docstrings
        info['docstring_info'] = docstrings.parse(info['docstring'])
    return info
fi.Info = _
