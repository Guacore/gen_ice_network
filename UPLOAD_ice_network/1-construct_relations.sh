echo "Start generating ET and TT relations..."
INFO_PATH="sourcefile/tagged_keywords_tfidf_onlyzh.json"
EMBD_PATH="sourcefile/tagged_keywords_vector.txt"
SAVE_PATH="relations/"

for REPK in 1 3 5 8 10
do
    for WEIGHTED in 0 1
    do
        for MAX_REPK in 10
        do
            ET_PATH=$SAVE_PATH"et_top"$REPK"_w"$WEIGHTED".edge"
            echo "Generating "$ET_PATH
            python3 gen_et.py -info $INFO_PATH -embd $EMBD_PATH -repk $REPK -max_repk $MAX_REPK -et $ET_PATH -w $WEIGHTED
        done
        for EXPK in 3
        do
            TT_PATH=$SAVE_PATH"tt_top"$REPK"x"$EXPK"_w"$WEIGHTED".edge"
            echo "Generating "$TT_PATH" and "$EXP_TT_PATH
            python3 gen_tt.py -embd $EMBD_PATH -et $ET_PATH -expk $EXPK -tt $TT_PATH -w $WEIGHTED
        done
    done
done
echo "Finished generating ET and TT relations."