# Problem Statement

There are a number of concerns about the way Spack CI is currently implemented:

- Build jobs are not requesting the appropriate amount of resources, leading to waste and contention with other jobs on the same pod
- Jobs with mismatched time estimates are being allocated to instances inappropriately, leading to situations where many small jobs complete, while a larger job uses the instance for the rest of its duration without using every available cycle
- We are currently retrying jobs up to 3 times in order to work around stochastic CI failures, which leads to more potential waste if the failure was valid. Instead, we would like to retry jobs if the cause of termination was resource contention.


In order to improve the framework, we must understand a few things about how builds behave:

- which packages are more variable in their resource usage
- what is the breakdown of resource request / resource usage

