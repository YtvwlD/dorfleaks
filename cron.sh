#!/bin/sh
./save.py
for WHAT in per_date per_weekday per_weekday_week per_user
do
        ./graph.py --what $WHAT --fetch_offline --to_file dorfleaks_$WHAT.html
done
