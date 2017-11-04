################################################################################
#        ______                    ______                            __        #
#       /  _/ /____  ____ ___     / ____/___  ____  ________  ____  / /_       #
#       / // __/ _ \/ __ `__ \   / /   / __ \/ __ \/ ___/ _ \/ __ \/ __/       #
#     _/ // /_/  __/ / / / / /  / /___/ /_/ / / / / /__/  __/ /_/ / /_         #
#    /___/\__/\___/_/ /_/ /_/   \____/\____/_/ /_/\___/\___/ .___/\__/         #
#                                                         /_/                  #
#            ______          __             __    ___                          #
#           / ____/___ ___  / /_  ___  ____/ /___/ (_)___  ____ _              #
#          / __/ / __ `__ \/ __ \/ _ \/ __  / __  / / __ \/ __ `/              #
#         / /___/ / / / / / /_/ /  __/ /_/ / /_/ / / / / / /_/ /               #
#        /_____/_/ /_/ /_/_.___/\___/\__,_/\__,_/_/_/ /_/\__, /                #
#                                                       /____/ credit: patorjk #
################################################################################

# Proj: Item Concept Embedding (ICE)
# File: gen_et.py
# Cont:
#   Func:
#       1) load_et_info                     2) load_embd_word
#       3) filter_word_by_embd              4) filter_entity_by_graph
#       5) gen_et_network

import json
import argparse
from tqdm import tqdm

def load_et_info(path):
    """ Load information required to generate an ET network.
    Param:
        parma1 [string] path to a json file of a list of dict where the preset
            key="id", "keyword", and "scores" and val=entity id, list of
            representative words, and list of descendingly ordered TF-IDF scores.
    Return:
        return1 [dict] where key=entity & val=list of 2-tuple of word and its
            TF-IDF score ordered descendingly by TF-IDF score.
    """
    et_info_dict = {}

    with open(path) as f:
        entity_dict_list = json.load(f)
        for entity_dict in entity_dict_list:
            et_info_dict[str(entity_dict["id"])] = list(zip(entity_dict["keywords"], entity_dict["scores"]))

    return et_info_dict

def load_embd_word(path):
    """ Load a list of words whose embeddings are available.
    Param:
        param1 [string] path to the word embedding file.
    Return:
        return1 [set] of words whose embeddings are available.
    Note:
        1) The first line of an embedding is assumed to be header and skipped.
    """
    word_set = set ()

    with open(path) as f:
        next(f) # assume the first line is header
        for line in f:
            entry = line.strip().split()
            word_set.add(entry[0])

    return word_set

def filter_word_by_embd(et_info_dict, path):
    """ Filter out representative words whose embeddings are not available.
    Param:
        param1 [dict] where key=entity & val=list of 2-tuple of word and its
            TF-IDF score ordered descendingly by TF-IDF score.
        param2 [string] path to the word embedding file.
    Return:
        return1 [dict] where key=entity & val=list of 2-tuple of word whose 
            embedding is available and its TF-IDF score ordered descendingly by
            TF-IDF score.
    Note:
        1) This function should be run PRIOR to filter_entity_by_graph() due to
            entity-filtering by the number of words is only valid given all
            considered words have embeddings.
    """
    rep_word_set = set()
    filt_word_set = set()
    embd_word_set = load_embd_word(path)

    # Step 1: Identify words without embeddings for filtering.
    for entity, tup_list in tqdm(et_info_dict.items()):
        kept_tup_list = [] 
        
        for tup in tup_list:
            rep_word_set.add(tup[0])
            if tup[0] in embd_word_set:
                kept_tup_list.append(tup)
            else:
                filt_word_set.add(tup[0])

        # Step 2: Remove words.
        et_info_dict[entity] = kept_tup_list

    # Step 3: Report filter stat.
    print("Filtered", len(filt_word_set),"words without embeddings out of", len(rep_word_set),"words.")

    return et_info_dict

def filter_entity_by_graph(et_info_dict, max_repk):
    """ Filter out entities with insufficient words for specified graph setting.
    Param:
        param1 [dict] where key=entity & val=list of 2-tuple of word and its
            TF-IDF score ordered descendingly by TF-IDF score.
        param2 [int] largest number of representative words to pick per entity
            amongst all considered graphs.
    Return:
        return1 [dict] where key=entity with sufficient representative words &
            val=list of 2-tuple of word and its TF-IDF score ordereed
            descendingly by TF-IDF score.
    Note:
        1) Running param2 on the largest setting considered in the experiment
            ensures identical entity set across graphs of all sizes.
        2) This function should be run AFTER filter_word_by_embd() due to
            entity-filtering by the number of words is only valid given all
            considered words have embeddings.
    """
    unfilt_size = len(et_info_dict)
    filt_entity_set = set()

    # Step 1: Indentify entities with insufficient words for filtering.
    for entity, tup_list in tqdm(et_info_dict.items()):
        if len(tup_list) < max_repk:
            filt_entity_set.add(entity)

    # Step 2: Remove entities.
    for entity in filt_entity_set:
        del et_info_dict[entity]

    # Step 3: Report filter stat.
    print("Filtered", len(filt_entity_set), "entities with less than", max_repk, "representative words out of", unfilt_size, "entities. Leaving", len(et_info_dict), "entities.")

    return et_info_dict

def gen_et_network(path, et_info_dict, repk, weighted):
    """ Generate and save the entity-text network.
    Param:
        param1 [string] path to save the ET network.
        param2 [dict] where key=entity and val=list of 2-tuple of word and its
            TF-IDF score ordered descendingly by TF-IDF.
        param3 [int] number of representative words to pick per entity.
        param4 [int] indicator of whether to use binary or loaded weights.
    """
    et_network = set() # remove duplicates

    if weighted == 1:
        for entity in tqdm(et_info_dict):
            for rep_word, weight in et_info_dict[entity][:repk]:
                et_network.add(entity + " " + rep_word + " " + str(weight))
    else:
        for entity in tqdm(et_info_dict):
            for rep_word, _ in et_info_dict[entity][:repk]:
                et_network.add(entity + " " + rep_word + " 1.0")

    with open(path, 'w') as f:
        f.write("\n".join(list(et_network)))

def main():

    # Step 1: Get arguments from users.
    parser = argparse.ArgumentParser(description="Generate entity-text (ET) network.")
    parser.add_argument("-load_info", help="Path to ET relations file")
    parser.add_argument("-load_embd", help="Path to word embeddings.")
    parser.add_argument("-repk", type=int, help="Number of representative words per entity for current graph.")
    parser.add_argument("-max_repk", type=int, help="Number of representative words per entity for the largest graph.")
    parser.add_argument("-save_et", help="Path to save the ET network.")
    parser.add_argument("-weighted", type=int, choices=[0,1], default=0, help="(Default) 0:unweighted / 1:weighted")
    args = parser.parse_args()

    print('Start generating entity-text relation edge list...')

    # Step 2: Construct the ET network:
    et_info_dict = load_et_info(args.load_info)
    et_info_dict = filter_word_by_embd(et_info_dict, args.load_embd)
    et_info_dict = filter_entity_by_graph(et_info_dict, args.max_repk)
    gen_et_network(args.save_et, et_info_dict, args.repk, args.weighted)

    print('Finished generating entity-text relation edge list!\n')

if __name__ == "__main__":
    main()
