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
# File: network_construction/gen_tt.py
# Cont:
#   Class:
#       1) IndexedMatrix
#   Func:
#       1) gen_indexed_matrix               2) load_rep_word
#       3) load_word_embd                   4) gen_tt_network

from sklearn.metrics import pairwise_distances
import json
import numpy as np
import argparse
from tqdm import tqdm

class IndexedMatrix():
    """ (duplicated)
    Store entities and their respective representations.
    """

    def __init__(self, items, rep_matrix):
        """ Constructor for IndexedMatrix.
        Param:
            param1 [self] reference to this object.
            param2 [list] of items.
            param3 [list] of lists of item-associated repr.
        """
        self.items = np.array(list(items)) # set will cause error later
        self.rep_matrix = np.array(rep_matrix).astype(np.float32)

def gen_indexed_matrix(words, rep_dict):
    """ Construct an IndexedMatrix object.
    Param:
        param1 [set] of 1-hot string entities.
        param2 [dict] where key=word & key=word embedding.
    Return:
        return1 [IndexedMatrix] object.
    """
    rep_matrix = [rep_dict[word] for word in words]
    return IndexedMatrix(words, rep_matrix)

def load_rep_word(et_path):
    """ Load a list of unique representative words from the entity-text network.
    Param:
        param1 [string] path to the entity-text network.
    Return:
        return1 [set] of unique representative words.
    Note:
        1) Assume every rep word in ET corresponds to relation(s) with exp words
            in TT. This ensure proper dimension size for matrix operation.
    """
    rep_word_set = set()

    with open(et_path) as f:
        for edge in f:
            entry = edge.strip().split()
            rep_word_set.add(entry[1])

    return rep_word_set

def load_word_embd(embd_path):
    """ Load a dictionry of words and respective embedding.
    Param:
        param1 [string] path to the word embedding file.
    Return:
        return1 [dict] where key=word & val=word embedding.
    Note:
        1) The first line of an embedding is assumed to be header and skipped.
    """
    word_embd_dict = {}

    with open(embd_path) as f:
        next(f) # assume the first line is header
        for line in f:
            entry = line.strip().split()
            word_embd_dict[entry[0]] = np.array(entry[1:]).astype(np.float32)

    return word_embd_dict

def gen_tt_network(tt_path, rep_word_set, word_embd_dict, expk, weighted):
    """ Generate and save the text-text network.
    Param:
        param1 [string] path to save the TT network. 
        param2 [set] of representative words.
        param3 [dict] where key=word & val=word embeddings.
        param4 [int] number of expanded words to pick per keyword.
        param5 [int] indicator of whether to use binary or loaded weights.
    """
    tt_network = set() # remove duplicates

    # Step 1: Find the cosine distance between every pair of word embeddings.
    mat = gen_indexed_matrix(rep_word_set, word_embd_dict)
    cos_mat = pairwise_distances(mat.rep_matrix, mat.rep_matrix, "cosine")

    # Step 2: Find expansion words for every representative word.
    for rep_idx in tqdm(range(len(mat.items))):
        exp_idx_list = cos_mat[rep_idx].argsort()[1:expk+1] # exclude rep word
        for exp_idx in exp_idx_list:
            if weighted:
                # Convert cos distance to cos similarity then shift and rescale.
                #   1) Shift from [-1,1] to [0,2] to ensure positiveness.
                #   2) Normalize to [0,1] to resemble probability.
                sim = str(1-cos_mat[rep_idx][exp_idx]/2) # cos sim = 1-cos dist
                tt_network.add(mat.items[rep_idx]+" "+mat.items[exp_idx]+" "+sim)
            else:
                tt_network.add(mat.items[rep_idx]+" "+mat.items[exp_idx]+" 1")

    with open(tt_path, "w") as f:
        f.write("\n".join(list(tt_network)))

def main():

    # Step 1: Get arguments from users.
    parser = argparse.ArgumentParser(description="Generate text-text (TT) network.")
    parser.add_argument("-load_embd", help="Path to pretrained word embeddings.")
    parser.add_argument("-load_et", help="Path to entity-text (ET) network.")
    parser.add_argument("-expk", type=int, help="Number of expanded words per representative words.")
    parser.add_argument("-save_tt", help="Path to save output TT network.")
    parser.add_argument("-weighted", type=int, choices=[0,1], default=0, help="(Default) 0:unweighted / 1:weighted.")
    args = parser.parse_args()

    print('Start generating text-text relation edge list...')

    # Step 2: Construct TT network:
    rep_word_set = load_rep_word(args.load_et)
    word_embd_dict = load_word_embd(args.load_embd)
    gen_tt_network(args.save_tt, rep_word_set, word_embd_dict, args.expk, args.weighted)

    print('Finished generating text-text relation edge list!\n')
    
if __name__ == "__main__":
    main()
