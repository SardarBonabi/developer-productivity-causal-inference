"""Representative reconstruction of the resume-described embedding workflow.

Research status and code availability
-------------------------------------
The research is currently under review. The full research code and data
are proprietary and are not distributed here. This file is a simplified
sample of the general workflow, not the complete research implementation
or a replication package.


Values below illustrate implementation choices, not recovered research settings.
Input is repository-level lists of languages from an approved pre-treatment
corpus. This excerpt clusters languages; assigning user segments requires a
separate aggregation rule and is intentionally outside the sample.
"""
import numpy as np
from gensim.models import Word2Vec
from scipy.cluster.hierarchy import linkage, cut_tree


def language_groups(repository_languages: list[list[str]], groups: int = 7):
    corpus = [sorted(set(languages)) for languages in repository_languages if languages]
    if len({language for row in corpus for language in row}) < groups:
        raise ValueError("Need at least one distinct language per requested group")
    # Cover the whole repository list so arbitrary language ordering does not
    # exclude co-occurrence pairs. Fixed seeds aid this representative example.
    model = Word2Vec(
        sentences=corpus, vector_size=32, window=max(map(len, corpus)),
        min_count=1, sg=1, workers=1, seed=42, epochs=20,
    )
    languages = sorted(model.wv.index_to_key)
    embeddings = np.array([model.wv[name] for name in languages])
    embeddings /= np.maximum(np.linalg.norm(embeddings, axis=1, keepdims=True), 1e-12)
    tree = linkage(embeddings, method="average", metric="cosine")
    labels = cut_tree(tree, n_clusters=groups).ravel()
    return dict(zip(languages, labels.tolist()))
