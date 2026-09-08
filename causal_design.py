"""Readable model contract, not the proprietary estimator implementation.

Research status and code availability
-------------------------------------
The research is currently under review. The full research code and data
are proprietary and are not distributed here. This file is a simplified
sample of the general workflow, not the complete research implementation
or a replication package.


A fixed-effects PPML backend is deliberately omitted. No OLS approximation is
presented as a substitute for the research estimator.
"""
from dataclasses import dataclass


@dataclass(frozen=True)
class PoissonDiD:
    outcome: str
    treatment_terms: tuple[str, ...] = ("italy_x_ban", "italy_x_restoration")
    controls: tuple[str, ...] = ("working_days",)
    fixed_effects: tuple[str, ...] = ("developer", "week")
    cluster: str = "developer"
    sample: str = "pre-treatment matched cohort"


SPECIFICATIONS = [
    PoissonDiD("code_development"),
    PoissonDiD("knowledge_sharing"),
    PoissonDiD("new_languages", controls=("working_days", "repository_controls")),
]
# E[Y_it | X] = exp(developer_FE + week_FE + beta_ban * italy_x_ban
#                  + beta_restoration * italy_x_restoration + controls)
# Match on pre-treatment covariates; retain matching weights where appropriate.
# A lead-lag design replaces the two treatment terms with relative-week terms,
# omitting the final pre-treatment week. Inspect uncertainty, not only point estimates.
