# Setup

0. Environment: Install `rye` and `git`.
Optional: `direnv`, `starship`.
On windows, `git`, `direnv`, and `starship` can be installed with `winget install <program>` (which is installed on every recent windows).
On Windows, you can use the `bash` that was installed as part of `git` to use `direnv` (as it does not support native Windows).

1. In the root, `rye sync`.
Then activate you can activate the environment that it created.
On Windows `.venv/Scripts/activate`.
If you have `direnv` installed, this is automated in [.envrc](../.envrc).

2. Develop!
