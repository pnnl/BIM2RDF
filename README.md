# BIM2RDF

Functionality used to convert building models in Speckle to ASHRAE S223 semantic models.
The operationalized version will be on [Speckle Automate](https://www.speckle.systems/product/automate).

Each top-level directory is a 'component' of the project.
Furthermore, the following dependencies were extracted as
generic stand-alone libraries:
[PyTQSHACL](https://github.com/pnnl/pytqshacl/),
[RDF-Engine](https://github.com/pnnl/rdf-engine/),
[JSON2RDF](https://github.com/pnnl/json2rdf/).


# Development

## Setup

```bash
> uv sync --all-packages
> uv run pre-commit install
# activate environment
> .venv/Scripts/activate
```
Make a [`.secrets.toml`](./.secrets.toml) file with
```toml
[speckle]
token = "yourtoken"
```

## Process

Follow [test](./test/) [instructions](./test/README.md).

# Usage

## [CLI](./src/bim2rdf/cli.py)
```bash
bim2rdf --help
```

## [Function](./src/bim2rdf/engine.py)

```python
from bim2rdf import Run
# initialize with a db
from pyoxigraph import Store
db = Store()
r = Run(db)
# execute with desired options
help(Run.run)
```

In development, a `.cache` directory will be created in the working directory
to save expensive expensive processing in general
but mainly to save Speckle query results.
Thus, the user must clear the cache to be able to access new data.
