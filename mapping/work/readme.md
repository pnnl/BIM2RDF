Where 'work' happens.

delete cache when needed.


# data mgt tbd

- how to manage "functionality" commits like the "mappings" vs. "data" commits made by dvc exp
- create a separate "data" branch? what is dvc exp "promote"?
- can keep one revit model and just "switch" between them?
- disable s223 "always-changed" b/c it's annoying
- create more managable table view
- metric: pass/fail


Main program is `python -m mapping.speckle`
if you are 'in' the (activated) virtualenv.
Else, you can `rye run mapping` from the `mapping` directory.



# File-based Data Flow and Management

..is managed by [dvc](./dvc.yaml).
`dvc` can also be run from outside the virtualenv `rye run dvc`.

Basic use:
<br>
From [this](./work) directory,
<br>
fill in [`params.yaml`](./work/params.yaml),
<br>
modify [mappings](./rules) if needed.
<br>
then just `dvc repro`,
<br>
then manage code, `git commit` changes and `push`,
<br>
then manage data, `dvc push`.



# Queries

..are either SELECT or CONSTRUCT types. (later maybe ASK for validation).

## Development

Use GraphDB or [oxigraph server](https://github.com/pchampin/oxigraph/tree/main/server) to develop queries.

Use the `--no-commit` in [DVC repro](https://dvc.org/doc/command-reference/repro) to not fill up your DVC cache when just developing.

## Checking

A query can processed/checked for project logic by a parsing program `python -m mapping.utils.query`.
The main check is that prefixes are defined either in the query itself or as part of a known list (`python -m mapping.utils.query prefixes`).
If a known prefix is used in a query, it will be added to the prefix list.
Otherwise, it has to be declared.
Also, the prefixes should be unique.
