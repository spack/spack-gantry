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

However, when doing this, I've stumbled upon packages that have unpredictable usage patterns that can swing from 200-400% of each other (with no discernible differences).

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

Microarchitecture is not used as a parameter in the model because it is not a strong predictor of resource usage. Additionally, we avoid limiting the sample size by not filtering past results on architecture, allowing for more accurate predictions.

Our analysis shows that the optimal number of builds to include in the prediction function is five, though we prefer four if the program will drop down to the next set in the list.

We do not use PR builds as part of the training data, as they are potential vectors for manipulation and can be error prone. The predictions will apply to both PR and develop jobs.
