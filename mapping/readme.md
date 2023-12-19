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
fill in [`params.yaml`](../params.yaml),
<br>
modify [mappings](../s223/) if needed.
<br>
then just `dvc repro`,
<br>
then manage code, `git commit` changes and `push`,
<br>
then manage data, `dvc push`.


# Queries

..are either SELECT or CONSTRUCT types. (later maybe ASK for validation).

## Development

Use GraphDB or [this utility](./tests/query.qmd).

## Checking

A query can processed/checked for project logic by a parsing program `python -m mapping.utils.query`.
The main check is that prefixes are defined either in the query itself or as part of a known list (`python -m mapping.utils.query prefixes`).
If a known prefix is used in a query, it will be added to the prefix list.
Otherwise, it has to be declared.
Also, the prefixes should be unique.

