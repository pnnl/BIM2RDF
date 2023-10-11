Main program is `python -m mapping.speckle`
if you are 'in' the (activated) virtualenv.
Else, you can `rye run mapping`.

Dataflow managed by [dvc](./dvc.yaml).
`dvc` can also be run from outside the virtualenv `rye run dvc`.

Basic use:
<br>
From [this](./) directory,
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
