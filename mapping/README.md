main contribution of bim2rdf are these rules 


## Dev

Use `python -m bim2rdf.queries sparql [--help]`
to evaluate templated sparql queries.
This will mainly be about making sure all variables are substituted for.
Use `--check=True` to check sparql syntax.
However, this will not check for variables embedded in strings
like `"Hello. My name is ${name}."`.
