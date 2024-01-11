# Context

Build definitions designated to be built within Spack CI are manually allotted to categories that reflect the resources a job is expected to consume. These amounts are used to allocate multiple jobs as efficiently as possible on a CI runner. Without accurate information about how much memory or CPU a compile will use, there is opportunity for misallocation, which can have effects on the following components of the CI system:

- Cost per job
- Build walltime
- Efficiency of VM packing
- Utilization of resources per job
- Build failures due to lack of memory
- Build error rate
- Throughput

Also, jobs with mismatched time estimates are being allocated to instances inappropriately, leading to situations where many small jobs complete, while a larger job uses the instance for the rest of its duration without using every available cycle. We are currently retrying jobs up to 3 times in order to work around stochastic CI failures, which leads to more potential waste if the error was valid. Instead, we would like to retry jobs if the cause of termination was resource contention.

Due to a problems of scale and inability to quickly and correctly determine the resource demand of a given build, we have decided that an automated framework that captures historical utilization and outputs predictions for future usage is the best path forward. 

With this setup, we can transition to a system where build jobs will request the appropriate amount of resources, which will reduce waste and contention with other jobs within the same namespace. Additionally, by amassing a vast repository of build attributes and historical usage, we can further analyze the behavior of these jobs and perform experiments within the context of the CI. For instance, understanding why certain packages are more variable in their memory usage during compilation, or determining if there is a "sweet spot" that minimizes resource usage but leads to an optimal build time for a given configuration.

## Current Handling of Resources

Each build job comes with a memory and CPU request. Kubernetes will use these numbers to allocate the job onto a specific VM. No limits are sent, meaning that a compilation could crowd out other jobs and that there are no consequences for going over what they are expected to utilize.
