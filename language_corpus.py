"""Representative corpus checks; research under review.

Full research code and data remain proprietary. This module illustrates a public
input contract, not the original language-selection rules or training corpus.
"""
from numbers import Integral


def prepare_language_corpus(repository_languages: list[list[str]], groups: int):
    """Deduplicate each repository's languages; preserve repeated repositories.

    Empty repository lists are excluded. Null rows, bare strings and blank labels
    fail explicitly instead of becoming character tokens or silent exclusions.
    """
    if isinstance(groups, bool) or not isinstance(groups, Integral) or groups < 1:
        raise ValueError("groups must be a positive integer")
    if not isinstance(repository_languages, (list, tuple)):
        raise ValueError("Expected a sequence of repository language lists")
    corpus = []
    for languages in repository_languages:
        if not isinstance(languages, (list, tuple)):
            raise ValueError("Each repository must contain a list of language labels")
        if any(not isinstance(name, str) or not name.strip() for name in languages):
            raise ValueError("Language labels must be nonblank strings")
        if languages:
            corpus.append(sorted(set(languages)))
    vocabulary = sorted({name for row in corpus for name in row})
    if len(vocabulary) < groups:
        raise ValueError("Need at least one distinct language per requested group")
    return corpus, vocabulary
