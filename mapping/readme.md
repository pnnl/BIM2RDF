`cd` to this directory and use `inv` to run program. go to 'work' for more structured ...work.

`dvc pull` to get data files.

if there's a problem with accessing storage, `dvc remote modify --local myremote account_key 'mysecret'` which changes [dvc local config](.dvc/config.local).
take 'mysecret' from azure storage referenced in the [setup](../dvc/tasks.py).
