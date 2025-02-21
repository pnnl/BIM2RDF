main contribution of bim2rdf are these rules 


## Dev

To make SPARQL queries more programmatic,
queries can be templated with `${varname}`.
Then, variable substitutions can be applied to get the desired query.

Use `python -m bim2rdf.queries sparql [--help]`
to evaluate templated sparql queries.
This will mainly be about making sure all variables are substituted for.
Use `--check=True` to check sparql syntax.
However, this will not check for variables embedded in strings
like `"Hello. My name is ${name}."`
as this would still be a valid string in sparql.

Use `python -m bim2rdf.queries default_substitutions`
to inspect defined variables.

Use `python -m bim2rdf.queries list`
to list defined queries.
