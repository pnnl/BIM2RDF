"""
query testing util.
"""


from pathlib import Path
def test(query: Path, dir: Path='tmp', ttl: Path=None, ):
    from pyoxigraph import Store
    if ttl:
        if Path(dir).exists():
            from shutil import rmtree
            rmtree(dir)
        s = Store(str(dir))
        s.bulk_load(str(ttl), 'text/turtle')
    else:
        s = Store(str(dir))
    
    _ = Path(query)
    _ = _.read_text()
    _ = s.query(_)
    import pandas as pd
    if hasattr(_, 'variables'):
        columns = [v.value for v in _.variables]
    else:
        # ie is a construct query
        columns = ['subject', 'predicate', 'object']
    _ = pd.DataFrame(
            tuple( #                                  nested triple
                tuple( (c.value if hasattr(c, 'value') else str(c))
                    for c in qs)
                for qs in _),
            columns=columns)
    with pd.option_context(
        'display.max_rows', None,
        'display.max_columns', None):
        print(_)

if __name__ == '__main__':
    import fire
    fire.Fire(test)
