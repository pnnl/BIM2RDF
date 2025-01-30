# BIM2RDF

Functionality used to convert building models in Speckle to ASHRAE S223 semantic models.
The operationalized version will be on [Speckle Automate](https://www.speckle.systems/product/automate).

Each top-level directory is a 'component' of the project.
Furthermore, the following dependencies were extracted as
generic stand-alone libraries:
* [PyTQSHACL](https://github.com/pnnl/pytqshacl/)
* [RDF-Engine](https://github.com/pnnl/pytqshacl/)
* [JSON2RDF](https://github.com/pnnl/json2rdf/)


# Development

```
> uv sync --all-packages
> uv run pre-commit install
```
Make a .secrets.toml file with
```toml
[speckle]
token = "yourtoken"
```