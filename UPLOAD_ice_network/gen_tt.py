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
# File: gen_tt.py
# Cont:
#   Class:
#       1) IndexedMatrix
#   Func:
#       1) gen_indexed_matrix               2) load_rep_word
#       3) load_word_embd                   4) gen_tt_relation

from sklearn.metrics import pairwise_distances
import json
import numpy as np
import argparse
from tqdm import tqdm

class IndexedMatrix():
    """ (duplicated)
    Store entities and their respective representations.
    """

    def __init__(self, items, embd_matrix):
        """ Constructor for IndexedMatrix.
        Param:
            param1 [self] reference to this object.
            param2 [list] of items.
            param3 [list] of lists of item-associated repr.
        """
        self.items = np.array(list(items)) # set will cause error later
        self.embd_matrix = np.array(embd_matrix).astype(np.float32)

def gen_indexed_matrix(words, rep_dict):
    """ Construct an IndexedMatrix object.
    Param:
        param1 [set] of 1-hot string entities.
        param2 [dict] where key=word & key=word embedding.
    Return:
        return1 [IndexedMatrix] object.
    """
    embd_matrix = [rep_dict[word] for word in words]
    return IndexedMatrix(words, embd_matrix)

def load_rep_word(et_rel_path):
    """ Load a list of unique representative words from ET relation.
    Param:
        param1 [string] path to load ET relation.
    Return:
        return1 [set] of unique representative words.
    Note:
        1) Assume every rep word in ET has exp words in TT. This ensures proper
            dimension for matrix operation.
    """
    rep_word_set = set()

    with open(et_rel_path) as f:
        for edge in f:
            entry = edge.strip().split()
            rep_word_set.add(entry[1])

    return rep_word_set

def load_word_embd(word_embd_path):
    """ Load a dictionry of words and respective embedding.
    Param:
        param1 [string] path to the word embedding file.
    Return:
        return1 [dict] where key=word & val=word embedding.
    Note:
        1) The first line of an embedding is assumed to be header and skipped.
    """
    word_embd_dict = {}

    with open(word_embd_path) as f:
        next(f) # assume the first line is header
        for line in f:
            entry = line.strip().split()
            word_embd_dict[entry[0]] = np.array(entry[1:]).astype(np.float32)

    return word_embd_dict

def gen_tt_relation(tt_path, rep_word_set, word_embd_dict, expk, weighted):
    """ Generate and save TT relation.
    Param:
        param1 [string] path to save TT relation.
        param2 [set] of representative words.
        param3 [dict] where key=word & val=word embeddings.
        param4 [int] number of expanded words to pick per keyword.
        param5 [int] indicator of whether to use binary or loaded weights.
    """
    tt_relation = set() # remove duplicates

    # Step 1: Find the cosine distance between every pair of word embeddings.
    rep_mat = gen_indexed_matrix(rep_word_set, word_embd_dict)
    exp_mat = gen_indexed_matrix(list(word_embd_dict.keys()), word_embd_dict)
    cos_mat = pairwise_distances(rep_mat.embd_matrix, exp_mat.embd_matrix, "cosine")

    # Step 2: Find expansion words for every representative word.
    if weighted:
        for rep_idx in tqdm(range(len(rep_mat.items))):
            exp_idx_list = cos_mat[rep_idx].argsort()[1:expk+1] # exclude rep word
            for exp_idx in exp_idx_list:
                # Convert cos distance to similarity then shift and rescale.
                #   1) Shift from [-1,1] to [0,2] to ensure positiveness.
                #   2) Normalize to [0,1] to resemble probability.
                sim = str(1-cos_mat[rep_idx][exp_idx]/2) # cos sim = 1-cos dist
                tt_relation.add(rep_mat.items[rep_idx]+" "+exp_mat.items[exp_idx]+" "+sim)
    else:
        for rep_idx in tqdm(range(len(rep_mat.items))):
            exp_idx_list = cos_mat[rep_idx].argsort()[1:expk+1] # exclude rep word
            for exp_idx in exp_idx_list:
                tt_relation.add(rep_mat.items[rep_idx]+" "+exp_mat.items[exp_idx]+" 1.0")

    # Step 3: Save TT relation.
    with open(tt_path, "w") as f:
        f.write("\n".join(list(tt_relation)))

def main():
    # Step 1: Get arguments from users.
    parser = argparse.ArgumentParser(description="Generate text-text (TT) relation.")
    parser.add_argument("-embd", help="Path to load word embeddings.")
    parser.add_argument("-et", help="Path to load entity-text (ET) relation.")
    parser.add_argument("-expk", type=int, help="Number of expanded words per representative words.")
    parser.add_argument("-tt", help="Path to save TT relation.")
    parser.add_argument("-w", type=int, choices=[0,1], default=0, help="(Default) 0:unweighted / 1:weighted.")
    args = parser.parse_args()

    print('Start generating TT relation...')

    # Step 2: Construct TT Network:
    rep_word_set = load_rep_word(args.et)
    word_embd_dict = load_word_embd(args.embd)
    gen_tt_relation(args.tt, rep_word_set, word_embd_dict, args.expk, args.w)

    print('Finished generating TT relation!\n')
    
if __name__ == "__main__":
    main()
