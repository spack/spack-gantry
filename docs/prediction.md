# Prediction

The basic idea here is: given metadata about a future build, recommend resource requests and limits, as well as number of build jobs.

The goal is that this eventually becomes a self-learning system which can facilitate better predictions over time without much interference.

At the moment, this isn't accomplished through some super fancy model. Here's our approach for each type of prediction:

**Requests**

Optimizing for the mean usage / predicted mean as close to 1 as possible.

Formula: avg(mean_usage) for past N builds.

**Limits**

For CPU: optimize for the number of cores for best efficiency
For RAM: optimize for lack of killing (max usage / predicted max < 1)

This one is a bit tricker to implement because we would like to limit OOM kills as much as possible, but we've thought about allocating 10-15% above historical maxima for usage.

We could also figure out the upper threshold by calculating

= skimpiest predicted limit / maximum usage for that job

However, when doing this, I've stumbled upon packages that have unpredictable usage patterns that can swing from 200-400% of each other (with no discernable differences).

More research and care will be needed when we finally decide to implement limit prediction.

### Predictors

We've done some analysis to determine the best predictors of resource usage. Because we need to return a result regardless of the confidence we have in it, we've developed a priority list of predictors to match on.

1. `("pkg_name", "pkg_version", "compiler_name", "compiler_version")`
2. `("pkg_name", "compiler_name", "compiler_version")`
3. `("pkg_name", "pkg_version", "compiler_name")`
4. `("pkg_name", "compiler_name")`
5. `("pkg_name", "pkg_version")`
6. `("pkg_name",)`

Variants are always included as a predictor.

Our analysis shows that the optimal number of builds to include in the prediction function is five, though we prefer four if the program will drop down to the next set in the list.

We do not use PR builds as part of the training data, as they are potential vectors for manipulation and can be error prone. The predictions will apply to both PR and develop jobs.

## Plan

1. In the pilot phase, we will only be implementing predictions for requests, and ensuring that they will only increase compared to current allocations.

2. If we see success in the pilot, we'll implement functionality which retries jobs with higher memory allocations if they've been shown to fail due to OOM kills.

3. Then, we will "drop the floor" and allow the predictor to allocate less memory than the package is used to. At this step, requests will be fully implemented.

4. Limits for CPU and memory will be implemented.

5. Next, we want to introduce some experimentation in the system and perform a [scaling study](#fuzzing).

6. Design a scheduler that decides which instance type a job should be placed on based on cost and expected usage and runtime.

## Evaluation

The success of our predictions can be evaluated against a number of factors:

- How much cheaper is the job?
- Closeness of request or limit to actual usage
- Jobs being killed due to resource contention
- Error distribution of prediction
- How much waste is there per build type?

## Fuzzing

10-15% of builds would be randomly selected to have their CPU limit modified up or down. This would happen a few times for the build, and see if we can find an optimal efficiency for the job, which would be used to define future CPU limit and number of build jobs.

We're essentially adding variance to the resource allocation and seeing how the system responds.

This is a strong scaling study, and the plot of interest is the efficiency curve.

Efficiency defined as cores/build time.
