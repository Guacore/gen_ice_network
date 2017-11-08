echo "Start generating ICE networks..."
RELA_PATH="relations/"
SAVE_PATH="networks/"

for REPK in 1 3 5 8 10
do
    for EXP in 1 3 5 8 10
    do
        for WEIGHTED in 0 1
        do
            echo "Start generating top"$REPK"x"$EXP"_w"$WEIGHTED" ICE network..."
            ICE_FULL_PATH=$SAVE_PATH"ice_full-top"$REPK"x"$EXP"_w"$WEIGHTED".edge"
            ICE_ET_PATH=$SAVE_PATH"ice_et-top"$REPK"_w"$WEIGHTED".edge"
            ICE_TT_PATH=$SAVE_PATH"ice_tt-top"$REPK"x"$EXP"_w"$WEIGHTED".edge"
            echo "Generating ICE network!"
            python3 gen_ice.py -et $RELA_PATH"et_top"$REPK"_w"$WEIGHTED".edge" -tt $RELA_PATH"tt_top"$REPK"x"$EXP"_w"$WEIGHTED".edge" -ice_full $ICE_FULL_PATH -ice_et $ICE_ET_PATH -ice_tt $ICE_TT_PATH -w $WEIGHTED
        done
    done
done
echo "Finished generating ICE networks!"
