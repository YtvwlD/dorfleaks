#!/bin/sh
./save.py || exit 1
for WHAT in per_date per_weekday per_weekday_week per_user
do
    for TEMPLATE in '' _dark
    do
        ./graph.py --what $WHAT --fetch_offline --template plotly$TEMPLATE \
        --to_file dorfleaks_$WHAT$TEMPLATE.html || exit 1
    done
done
exit 0
