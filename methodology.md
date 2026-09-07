# Measurement and causal design

## From traces to outcomes

Code development combines repository creation, commits, and pull requests. Knowledge sharing combines reviews, issues, and discussions. Skill acquisition is operationalized as first observed use of a programming language in a developer's repository history. Historical coverage is essential: starting the history at the estimation window would falsely classify previously used languages as new.

The sample consolidates language detection into an explicit transformation with named inputs, removing positional column selection, global counters, hard-coded paths, and repeated output-writing steps. It pools simultaneous repository timestamps so tie order does not determine first-use attribution.

## Identification

The study compares Italian developers with matched developers in France and Portugal around the temporary suspension and restoration of ChatGPT access. Matching uses pre-treatment characteristics. Developer fixed effects absorb time-invariant developer differences; week fixed effects absorb common time shocks. Working-day controls account for calendar differences. Poisson estimation accommodates nonnegative, skewed activity measures, and developer clustering addresses within-developer dependence.

The treatment-by-suspension and treatment-by-restoration coefficients are distinct. The interpretation of exp(beta) minus one is a proportional change relative to the model's baseline, not an absolute change in counts. Lead-lag estimates assess pre-treatment patterns; failure to reject pre-trends does not prove parallel counterfactual trends.

## Segmentation

The completed research included K-Means on structural features and skip-gram language embeddings with hierarchical clustering to derive seven user-technology segments. The public embedding sample demonstrates the language-grouping component. It does not recreate the original hyperparameters, corpus filters, or user-assignment rules. Repository histories, technology exposure, and experience provide ways to investigate why average effects differ across users.

## Scope of inference

The findings concern this setting and access interruption. Actual individual ChatGPT use is not directly observed. Country assignment, other tools, concurrent shocks, and the operational nature of the learning measure constrain interpretation. Repository coverage and matching restrictions distinguish the study's estimation samples from the broader collection resource.
