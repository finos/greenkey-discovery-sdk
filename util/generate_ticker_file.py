#!/usr/bin/env python3

import sys
from fire import Fire
import pickle


def clean_entity(entity):
    """
    Clean formatting from an entity
  
    >>> clean_entity('Test')
    'test'
    >>> clean_entity('ABC Holdings')
    'abc holdings'
    """
    return entity.lower()


def remove_entity_from_list(unique_list, i):
    """
    Removes all instances of a particular entity from a list
  
    >>> remove_entity_from_list(['test', 'test', 'three'], 1)
    ['three']
    """
    return [x for x in unique_list if x != unique_list[i]]


def patch_entity_list_duplicates(unique_list, original_list, i):
    """
    Updates a list containing duplicates at index i with longer entities from the original list
  
    >>> patch_entity_list_duplicates(['test', 'test', 'three'], ['test one', 'test two', 'three'], 1)
    ['test one', 'test two', 'three']
    >>> patch_entity_list_duplicates(['test', 'test', 'three'], ['test', 'test', 'three'], 1)
    WARNING: Could not remove duplicate test with entity ['test']
    WARNING: Could not remove duplicate test with entity ['test']
    ERROR: More than one duplicate could not be resolved at entity 2 of 3
    ['test', 'test', 'three']
    >>> patch_entity_list_duplicates(['test', 'test', 'three'], ['test', 'test one', 'three'], 1)
    WARNING: Could not remove duplicate test with entity ['test']
    ['test', 'test one', 'three']
    >>> patch_entity_list_duplicates(
    ... ['a', 'china', 'b', 'china', 'c', 'china'],
    ... ['a', 'china sxt pharma', 'b', 'china kempei', 'c', 'china inc'], 1)
    ['a', 'china sxt', 'b', 'china kempei', 'c', 'china inc']
    """
    current_entity = unique_list[i]
    indices_to_change = [
        index for index in range(len(unique_list))
        if unique_list[index] == current_entity
    ]

    possible_conflicts = []
    for index in indices_to_change:
        original_entity = original_list[index].split(' ')

        if len(original_entity) < len(current_entity.split(' ')) + 1:
            print("WARNING: Could not remove duplicate {0} with entity {1}".format(
                unique_list[i], original_entity))
            possible_conflicts.append(index)
        else:
            unique_list[index] = ' '.join(
                original_entity[:len(current_entity.split(' ')) + 1])

    if len(possible_conflicts) > 1:
        print(
            "ERROR: More than one duplicate could not be resolved at entity {0} of {1}".
            format(i + 1, len(original_list)))

    return unique_list


def update_entity_working_list(original_entities, seen_entities, entity_working_list, i):
    if entity_working_list[i] in seen_entities:
        first_duplicate = seen_entities.index(entity_working_list[i])
        entity_working_list = patch_entity_list_duplicates(entity_working_list,
                                                           original_entities, i)
        seen_entities[first_duplicate] = entity_working_list[first_duplicate]

    return seen_entities, entity_working_list


def create_unique_minimum_entities(entities):
    """
    Retuns an entity list where each entity is as short
    as possible while maintaining a unique list
  
    >>> create_unique_minimum_entities(['abc one company', 'abc two company', 'def three company'])
    ['abc one', 'abc two', 'def']
    """
    original_entities = entities
    unique_entity_working_list = [e.split(' ')[0] for e in original_entities]

    while True:
        seen_entities = []
        i = 0
        while i < len(unique_entity_working_list):
            seen_entities, unique_entity_working_list = update_entity_working_list(
                original_entities,
                seen_entities,
                unique_entity_working_list,
                i,
            )
            seen_entities.append(unique_entity_working_list[i])
            i += 1

        if len(seen_entities) == len(unique_entity_working_list):
            break

    return unique_entity_working_list


def entities_to_rockets(entity_pairs, case_insensitive=False):
    """
    Convert entity pairs to rocket replacements
  
    >>> entities_to_rockets([['Test','TST']], True)
    ['test -> TST']
  
    >>> entities_to_rockets([['Test','TST']])
    ['Test -> TST']
    """
    entities = [clean_entity(e[0]) if case_insensitive else e[0] for e in entity_pairs]
    entities = create_unique_minimum_entities(entities)

    tickers = [e[1].strip() for e in entity_pairs]

    assert len(entities) == len(tickers)

    return ["{0} -> {1}".format(x, y) for x, y in zip(entities, tickers)]


def tickers_to_rockets(entity_pairs):
    """
    Converts tickers to rocket replacements
  
    >>> tickers_to_rockets([['Test','TST']])
    ['t s t -> TST']
    """
    tickers = [e[1].strip() for e in entity_pairs]
    entities = [' '.join(list(e.lower())) for e in tickers]

    return ["{0} -> {1}".format(x, y) for x, y in zip(entities, tickers)]


def generate_ticker_file(filename,
                         case_insensitive=False,
                         pickled=False,
                         tickers_only=False):
    """
    * Create a companies.csv file with two columns for company name and ticker: company name, ticker
    corp one, ABC
    corp two, DEV
    three, GHI
  
    * Generate a company -> ticker mapping:
    python util/generate_ticker_list.py companies.csv
    and you get a file like this called companies.txt:

    corp two -> DEV
    corp one -> ABC
    three -> GHI
  
    * Generate a ticker -> ticker mapping:
    python util/generate_ticker_file.py companies.csv --tickers_only and you'll get a file like this called companies_tickers.txt:

    d e v -> DEV
    a b c -> ABC
    g h i -> GHI
  
    If you wish to use both files for entity definitions, simply combine them.
    cat companies_tickers.txt >> companies.txt
    """
    entity_pairs = [
        e.split(',') for e in list(set([x.strip() for x in open(filename)][1:]))
    ]

    output_file = filename

    if tickers_only:
        entities = tickers_to_rockets(entity_pairs)
        output_file = filename.replace('.csv', '_tickers.csv')
    else:
        entities = entities_to_rockets(entity_pairs, case_insensitive)

    if pickled:
        with open(output_file.replace('.csv', '.p'), 'wb') as f:
            pickle.dump({"data": '\n'.join(entities)}, f)
    else:
        with open(output_file.replace('.csv', '.txt'), 'w') as f:
            print('\n'.join(entities), file=f)


if __name__ == "__main__":
    Fire(generate_ticker_file)
