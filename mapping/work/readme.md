Where 'work' happens. Refer to `dvc` (which just wraps the `inv` commands).


Basic use:
<br>
From [this](..) directory,
<br>
fill in [`params.yaml`](../params.yaml),
<br>
put your data and mapping files according to ['dvc.yaml'](../dvc.yaml),
<br>
then just `dvc repro`,
<br>
finally, `git commit` changes and push.




<br><br><br>
---
dev note: could be its own env-level "workdir", mapping-work, since its it just needs the 'core' and dvc.
