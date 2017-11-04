echo "Start generating ET and TT relation edge lists..."
INFO_PATH="../sourcefile_for_gen/keywords-tfidf-onlyzh.json"
EMBD_PATH="../sourcefile_for_gen/keywords-vector.txt"
SAVE_PATH="relation_edge_list/"

for REPK in 1 3 5 8 10
do
    for WEIGHTED in 0 1
    do
        for MAX_REPK in 10
        do
            ET_PATH=$SAVE_PATH"et_top"$REPK"_w"$WEIGHTED".edge"
            echo "Generating "$ET_PATH
            python3 gen_et.py -load_info $INFO_PATH -load_embd $EMBD_PATH -repk $REPK -max_repk $MAX_REPK -save_et $ET_PATH -weighted $WEIGHTED
        done
        for EXPK in 3
        do
            TT_PATH=$SAVE_PATH"tt_top"$REPK"x"$EXPK"_w"$WEIGHTED".edge"
            echo "Generating "$TT_PATH
            python3 gen_tt.py -load_embd $EMBD_PATH -load_et $ET_PATH -expk $EXPK -save_tt $TT_PATH -weighted $WEIGHTED
        done
    done
done
echo "Finished generating ET and TT relation edge lists."
