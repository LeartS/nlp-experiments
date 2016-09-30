#! /usr/bin/env python3

import argparse
import itertools

from nltk.corpus import wordnet as wn


def combined_path_similarity(keywords):
    """
    Calculates the path_similarity between all pairs of keywords and returns
    the product.
    """
    score = 1
    for k1, k2 in itertools.combinations(keywords, 2):
        score *= (k1.path_similarity(k2) or 0)
    return score


def disambiguate_keywords(keywords, scoring_function):
    """
    Returns all possible combination of senses, from the most likely
    to the least.
    Return a list in the format:
    [
        ((synset keyword 1, synset keyword 2, ...), score),  # most likely
        ((synset keyword 1, synset keyword 2, ...), score),  # 2nd-most likely
    ]
    """
    all_synsets = [wn.synsets(k) for k in keywords]
    return sorted(
        [(synset_combination, scoring_function(synset_combination))
         for synset_combination in itertools.product(*all_synsets)],
        key=lambda x: x[-1],
        reverse=True
    )


def print_combination(keywords, synsets, score):
    print('--- {} ---'.format(', '.join([s.name() for s in synsets])))
    print('Score: ', score)
    for keyword, synset in zip(keywords, synsets):
        print(' * {}: {}'.format(keyword, synset.definition()))
    print()


if __name__ == '__main__':
    # ARGUMENT PARSING
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'keywords', nargs='+', type=str,
        help='The keywords to disambiguate')
    parser.add_argument(
        '--best', type=int, default=3,
        help='Number of best senses to show')
    parser.add_argument(
        '--worst', type=int, default=0,
        help='Number of worst senses to show')
    arguments = parser.parse_args()

    # STUFF HAPPENS HERE
    keywords = arguments.keywords
    results = disambiguate_keywords(
        arguments.keywords, combined_path_similarity)
    total_score = sum(r[-1] for r in results)  # used to normalize results

    # OUTPUT
    if arguments.best:
        print('########## BEST #########')
        for best_synset_comb, score in results[:arguments.best]:
            print_combination(
                keywords, best_synset_comb, score*100 / total_score)

    if arguments.worst:
        print('\n\n########## WORST #########')
        for worst_synset_comb, score in results[len(results)-arguments.worst:]:
            print_combination(
                keywords, worst_synset_comb, score*100 / total_score)
