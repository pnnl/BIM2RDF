# I. Workflow

This repository represents a 'workspace' for both source code (both 'library' type code and scripts, referred to as just 'code' from here on) _and_ non- source code (data and generated assets, referred to as just 'files' from here on).
In addition, execution environments and workflow tasks are managed as well.

* **Code**, representing fuctionality, configuration, and file _references_ is managed by `git`.
* **Files** are managed by `dvc` ([data science version control](http://dvc.org)).
* **Environments** are managed by [`conda`](https://docs.conda.io) and [`conda devenv`](https://conda-devenv.readthedocs.io).
* **Tasks** are managed by [`invoke`](http://docs.pyinvoke.org).

## Structure

![image](https://user-images.githubusercontent.com/3588248/175333804-f3d5bf61-9e05-4073-948e-fbf09702ba89.png)


The workflow manages a 'work directory' (workdir) concept: some separated-out unit of work.
It could be a module/library or a one-off experiment.
To keep things as simple as possible, workdirs are the folders directly under the root of the workspace.
The workdir structure is flat so collaborators can immediately identify units of work.
Nonetheless, each workdir can have its own directory hierarchy obviously.

### Development environment file

A [environment.devenv.yml](./environment.devenv.template.yml) is in each workdir holding development environment configuration.
The configurtion is specified by environment variables and dependencies.

** 'Internal' Dependencies **
Internal dependencies are other work dirs in the project.
They are specified in the 'includes' section, a directive to include _other_ development environment files.

** 'External' Dependencies **
External dependencies are specified as a list under the 'dependencies' section.
These are 'normal' conda dependency specifications except that some can be excluded from being installed in an environment which includes the environment file in which they are defined.
This is useful to exclude devlopment tools (like test frameworks and code linters) from being installed in an dependent environment.
In addition to conda-supported 'pip'-type dependencies, a special 'cmd' type dependency allows for executing arbitrary (installation) commands.
For each dependency type, installation order can be forced by prefixing the installer with a number.
For example, `pip` can be `0pip` to put it at the top of the execution list (a hack to undo the underlying conda devenv behavior).


## Scripts

Script files placed in the 'scripts' directory will be processed to produce wrapped executables.
Currently, .py, .bat, and .sh scripts are supported in addition to a special .cmdlines.
Scripts beginning with 'setup' will be processed and executed as part of an automated setup process.
However, setup scripts should be limited to light-weight tasks such as configuration (not installation).


## Process

The workflow is formalized by the tasks that are defined in the `project` command.
The tasks (try to) align code, files, and execution environments.
The tasks aid the following development process.

0. Activate project environment: `> conda activate prefix-project`.

1. Initialize work directories.

    The `work-on` task (`> project work-on <workdirname>`) is intended to be an entry point into work by automating the following process.

    0. Initialization of

        *Directory contents.*
        A work directory (with environment file) will be created if one does not exist.

        *Environment.*
        A 'default' environment will be created according the the [environment.devenv.yml](./environment.devenv.template.yml) template.

    1. Environment check

        Once a workdir has been initialized, the task will instruct to switch to the workdir environment and directory.

2. Manage environment.

    Declare the dependencies by modifying the environment.devenv.yml (in the created directory).
    See conda [devenv documentation](https://conda-devenv.readthedocs.io/en/latest/).

    Invoke `project work-on <workdirname>` from the project environment to make changes to the environment.

3. Manage source and file references.

    Manage (source) code (only) with `git` and keep data and generated assets such as notebooks, intermediate files, documentation, visualizations, and model files out of source control.
    This separation is enforced with a restrictive [.gitignore](.gitignore);
    All files are ignored except patterns that are considered (source) code.

    `dvc run` is useful here to declare an execution consisting of input files, commands, and output files which will generate a .dvc file to be source controlled.
    `dvc add` is useful to just add (and manage) files.
    Use `> dvc pull <dvcfile>` to obtain input files.

    It may be useful to, again, create a branch to represent different versions of the work.

3. Reproduce.

    Reproduction of an execution is achieved when input files, commands, and the execution environment are specified.
    Through a .dvc file, `dvc repro` manages input files and commands (but not the execution environment directly).
    Now, the environment.*.yml files should reflect the development environment.
    So the way to ensure reproduction of the execution is to recreate the development environment as follows:
    1. `> project reset <workdir>`
    2. `> dvc repro <dvcfile>`.

4. Commit source and files.

    The usual `git commit` command has been modified to prepend the commit message with '[workdir]' to help identify top-level work.

    After committing code, representing functionality and an execution process, generated assets should be shared with a `dvc push`.


# II. Development Environment Setup

0. **Obtain source**

    Enter 'base' environment: `> conda activate base`.
    Then obtain source with
    `> git clone https://repo.git prefix`.
    <br>
    The source was cloned into the 'workspace' directory even though it's called 'workspace-code' to emphasize that code and non-code will combine in the directory.

1. **Bootstrap**

    Executing [bootstrap.sh](./bootstrap.sh) and [bootstrap.bat](./bootstrap.bat) for Mac/Linux and Windows, respectively, will initialize the project.


2. **Check project tools**

    After entering the project development environment, with `> conda activate prefix-project`, check that you can list development [tasks](./project/tasks/tasks.py) with: `> project -l`.
    <br>
Use `-h` before the task name to learn about the task like:
    
    ```
    (prefix-project) > project -h project.info.work-dir-list
    Usage: inv[oke] [--core-opts] list-work-dirs [other tasks here ...]
    
    Docstring:
    Lists work directories

    Options:
    none
	```

