from invoke import task


@task
def get_ontologies(ctx):
    from ontologies import init
    init()




from pathlib import Path
from project import activated_workdir

@task
def map(ctx, bdg, ontology, db_file=activated_workdir / 'work' /'db.sqlite'):
    from pathlib import Path
    import mapping.mapping as m

    sr = m.SQLRDFMapping.make((bdg, ontology, m.SQLiteDB( db_file) , ))
    sr.map(db_file.parent)

