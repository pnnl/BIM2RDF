# Semantic Interoperability

The purpose of this codebase is to produce
validated design data mappings
and documentation.

## Structure

The codebase is a standard Python project managed by [Rye](https://rye-up.com/).
Each top-level folder is a component or workspace.
* There should be a readme in each folder.
* Each component should have a configuration program: `python -m <component>.config`. `python -m project.config` should trigger all.
* There may be a command line interface for functionality defined in modules.

### Tools

These tools are standardized due to their high utility.

* Source code is managed by [`git`](https://git-scm.com/).
* Non-source code files (like data) and pipelines are managed by [dvc](http://dvc.org).
As such the [.gitignore](./.gitignore) only allows source code files.
* Documentation is generated with [Quarto](https://quarto.org/).
* dev: [fire](https://github.com/google/python-fire) to create command line interfaces

## Setup

### Administration


* Azure:
    * **dvc storage**: check access to [container](https://portal.azure.com/#view/Microsoft_Azure_Storage/ContainerMenuBlade/~/overview/storageAccountId/%2Fsubscriptions%2F945ae372-bdd3-442f-83b2-6f5f6ff1eee2%2FresourceGroups%2Fprototypemodels%2Fproviders%2FMicrosoft.Storage%2FstorageAccounts%2Fprototypemodelsstorage/path/dvc/etag/%220x8DA87B93CA25E97%22/defaultEncryptionScope/%24account-encryption-key/denyEncryptionScopeOverride~/false/defaultId//publicAccessVal/None).
    * **secrets**: check access to [secrets](https://portal.azure.com/#@PNNL.onmicrosoft.com/resource/subscriptions/945ae372-bdd3-442f-83b2-6f5f6ff1eee2/resourceGroups/prototypemodels/providers/Microsoft.KeyVault/vaults/semint/secrets).

* Speckle: create API key. The key will be used to [programmatically access Speckle](https://gitlab.pnnl.gov/conlight/semint/-/blob/fb2960ab43177540daacb3e5be4eaaecd6fae525/speckle/src/speckle/requests.py#L3).

### Code

The Python-based setup is highly automated
but non-Python tools have to be installed separately.

0. **Before** getting code, install:
    * `rye`
    * `git`. Use your system manager: `winget` on Windows, `homebrew` on Mac.
    * `quarto`. Pre-release.
    * optional: devenv

1. **Get code**: `git clone --recursive https://gitlab.pnnl.gov/conlight/semint.git`.
Clone under your personal folder outside of your OneDrive. On Windows this is c:\Users\myusername.

2. **Setup**:
    1. Install **dependencies**: cd into `semint`. Then `rye sync`.
    2. **configure**: `python -m project.config`


## Workflow

tbd but standard git branching is used as a mechanism to isolate code changes from the 'main' branch.
