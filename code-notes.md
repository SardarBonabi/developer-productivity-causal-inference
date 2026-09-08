# Sample code and provenance

> **Research status and code availability:** The research is currently under review. The full research code and data are proprietary and are not distributed here. The public code consists only of selected, simplified samples of the general workflow; it is not the complete research implementation or a replication package.

The research accomplishments are described from Sardar Fatooreh Bonabi's account of his completed work. The manuscripts provide study context and findings. This release selectively illustrates methods without distributing the full proprietary implementations.

| File | Relationship to the research |
|---|---|
| collection.py | Representative rewrite of pagination, retries, persistence, and restart logic visible in the collection archive. Production concurrency and database adapters are omitted. |
| panel_features.py | First-use logic refactored from the supplied language-processing script; activity aggregation is a representative consolidation. Timestamp tie handling is an explicit public-example adaptation. |
| technology_segments.py | Reconstructed example of the embedding and clustering work described in the resume; original implementation and hyperparameters are proprietary. |
| causal_design.py | Declarative summary of the manuscript model, not an executable PPML estimator. |

## What was refactored

The public samples replace repeated country/partition scripts with parameterized functions; separate I/O from analytical logic; use descriptive variables and explicit model contracts; and remove embedded paths, credentials, debugging output, and confidential records. Illustrative safeguards and settings added in this release are not claims about the historical implementation.

## Reading the examples

The samples are Python source intended to be read on GitHub. There is no installation or replication requirement. External library imports indicate the methods being illustrated, not a locked production environment. No private data, real identifiers, model artifacts, or empirical prediction files are included. The methods notes explain where details are omitted and distinguish study results from illustrative code.

Original code and research data remain proprietary. No open-source license is granted by this showcase.
