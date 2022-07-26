from invoke import task


@task
def get_ontologies(ctx):
    from ontologies import init
    init()


from pathlib import Path
from project import activated_workdir


@task
def map(ctx, ontology, bdg=None,  db_file=str(activated_workdir / 'work' /'db.sqlite')):
    # db
    db_file = Path(db_file)
    if not db_file.exists(): raise ValueError('db file doesnt exist')
    # bdg
    if not bdg: bdg = db_file.stem

    import mapping.mapping as m
    sr = m.SQLRDFMapping.make((bdg, ontology, m.SQLiteDB( db_file) , ))
    sr.map(db_file.parent)

