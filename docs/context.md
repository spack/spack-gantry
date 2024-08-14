# Context

Build definitions compiled in Spack's CI are manually allotted to categories that reflect the resources expected to be consumed. These amounts are used to allocate multiple jobs as efficiently as possible on a CI runner. Without accurate information about how much memory or CPU a compile will use, there is opportunity for misallocation, which can have effects on the following components of the CI system:

- Cost per job
- Build walltime
- Efficiency of VM packing
- Utilization of resources per job
- Build failures due to lack of memory
- Build error rate
- Overall throughput

Also, jobs with mismatched time estimates are being allocated to instances inappropriately, leading to situations where many small jobs complete, while a larger job uses the instance for the rest of its duration without using every available cycle. We are currently retrying jobs up to 3 times in order to work around stochastic CI failures, which leads to more potential waste if the error was valid. Instead, we would like to retry jobs if the cause of termination was resource contention.

Due to a problems of scale and inability to manually determine the resource demand of a given build, we have decided that an automated framework that captures historical utilization and outputs predictions for future usage is the best course of action. 

With this setup, we can transition to a system where build jobs will request the appropriate amount of resources, which will reduce waste and contention with other jobs within the same namespace. Additionally, by amassing a vast repository of build attributes and historical usage, we can further analyze the behavior of these jobs and perform experiments within the context of the CI. For instance, understanding why certain packages are more variable in their memory usage during compilation, or determining if there is a "sweet spot" that minimizes resource usage but leads to an optimal build time for a given configuration (i.e. a scaling study).

A corollary to this is building a system that handles job failures with some intelligence. For instance, if a build was OOM killed, `gantry` would submit the same job and supply it with more memory. Jobs that fail due to other reasons would be resolved through other channels.

## Current resource allocation

Each build job comes with a memory and CPU request. Kubernetes will use these numbers to allocate the job onto a specific VM. No limits are sent, meaning that a compilation could crowd out other jobs and that there are no consequences for going over what they are expected to utilize.

-----

To illustrate the problem, let's go through some usage numbers (across all builds):

**Memory**

- avg/request = 0.26
- max/request = 0.64

**CPU**

- avg/request = 1.25
- max/request = 2.69

There is a lot of misallocation going on here. As was said above, limits are not enforced, so request is the closest we're going to get to a useful comparison of usage. Bottom line, we are using a lot less memory than we request, and more CPU than we ask for.
