"""Representative reconstruction of the embedding workflow.

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
from embedding_geometry import normalize_embeddings
from language_corpus import prepare_language_corpus


def language_groups(repository_languages: list[list[str]], groups: int = 7):
    corpus, vocabulary = prepare_language_corpus(repository_languages, groups)
    if len(vocabulary) == 1:
        return {vocabulary[0]: 0}
    from gensim.models import Word2Vec
    from scipy.cluster.hierarchy import linkage, cut_tree

    # Cover the whole repository list so arbitrary language ordering does not
    # exclude co-occurrence pairs. Fixed seeds aid this representative example.
    model = Word2Vec(
        sentences=corpus, vector_size=32, window=max(map(len, corpus)),
        min_count=1, sg=1, workers=1, seed=42, epochs=20,
    )
    languages = sorted(model.wv.index_to_key)
    embeddings = normalize_embeddings([model.wv[name] for name in languages])
    tree = linkage(embeddings, method="average", metric="cosine")
    labels = cut_tree(tree, n_clusters=groups).ravel()
    return dict(zip(languages, labels.tolist()))
