# hydraconda pitch
technical: [readme](./project/readme.md)


# NEED
Computation-based research is often messy, non-linear, and highly exploratory. At the same time, there is a need for developed code to be reproducible for scientific integrity and to aid  collaboration. Furthermore, long-term maintainability of computation-based projects benefit from modularization.

Software engineering tools can help but often involve an inappropriate level of formality and tool introduction; Creating programming-language specific 'libraries' of software to organize and distribute code is often too cumbersome and unnecessary. The first concern of scientific software is often just reproduciblity. How can computational code be advanced without getting bogged down by software engineering rigor?



_Note_: One needs to also manage code (itself) as well as data for more thorough reproducibility. This effort only addresses managing computational environments. Managing code (itself) and data are essentially solved problems that can be addressed with established tools.

 

# APPROACH
Develop a way of creating composable functionality by organizing reproducible computational environments (instead of focusing on organizing functionality as  programming-language specific 'libraries' of code). Environments are a more accommodating 'container' of software that can be made to 'compose' in advantageous ways.

# BENEFIT
The benefit of the approach derives from the ability to have multiple, yet related, reproducible environments coexisting (thus cooperating). This (one) approach can yield the following interesting functionality:

* **High-level data processing**: each 'stage' in the data 'pipeline' can be its own environment that is quite different from other stages
* **Controlled Notebook computing**: The main computational notebook program (such as Jupyter) can be in its own (centrally-managed) environment while computation kernels can exist in separate environments
* **Reduces the need to containerize**. Sophisticated setups can be made without having to 'Dockerize' as the computational environment is the container.
* **Accommodates heterogeneous computation**. By managing executables in environments, there is no technical reason to insist on having one computation system. For example, R and Python can be in the same or different environments; the focus is on establishing a certain functionality in an environment regardless of the execution system.
* **Lightweight modularization**. Code modularization can be addressed as a matter of just configuration instead of having to worry about creating a 'library' (for distribution). A project can advance by modularizing code as needed.
* **Easy deployments to cloud**. Since the organization is reproducible, tapping into cloud resources uses the same code as local execution.

In general, the above benefits translate into higher productivity, scientific integrity, and collaboration especially for long-running projects. In a way, each project can assemble and establish its own 'platform' using external resources (like cloud) and/or proprietary tools only as needed.

 

# COMPETITION
Software build system exist to create 'packages' (to install in a given environment) but not to build related environments.

# SUCCESS CRITERIA
A computational researcher should be able to issue only a few commands in order to acquire a 'baseline'  of general functionality for his or her project. This can then be easily extended by learning about the framework through documentation.
