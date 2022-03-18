from invoke import task
from ontologies import get


@task
def get_ontologies(ctx):
    from ontologies import get
    get()



@task
def clean(what):
    pass