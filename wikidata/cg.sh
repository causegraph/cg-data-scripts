#!/bin/bash

DATE_SHORT="$(date +%Y%m%d)"
#echo "CauseGraph: starting Wikidata dump download: $(date --utc +%Y%m%dT%H:%M:%S)"
# the .gz is 50% larger than the .bz2, but it's ready sooner and unzips faster
#wget --no-if-modified-since -N https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.gz
#echo "CauseGraph: dump downloaded: $(date --utc +%Y%m%dT%H:%M:%S)"
#gunzip -k latest-all.json.gz
#echo "CauseGraph: dump decompressed: $(date --utc +%Y%m%dT%H:%M:%S)"

WORKSPACE="workspace-$(date --utc +%Y%m%dT%H:%M:%S)"
mkdir -p $WORKSPACE
# cp wd2cg.py $WORKSPACE
# cp wd_constants.py $WORKSPACE
cp *.py $WORKSPACE
# cp makengraph.js $WORKSPACE
# cp fix_labels.py $WORKSPACE
cp filter.json $WORKSPACE
cd $WORKSPACE
zcat /run/media/jamie/extra/data/wikimedia/latest-all.json.gz | ./wd2cg.py
echo "CauseGraph: starting additional python scripts"
./back_edge_finder.py 150 > back_edges_150_$DATE_SHORT.txt
./date_flagger.py > flagged_dates_$DATE_SHORT.txt
cat flagged_dates_$DATE_SHORT.txt
#./cg_analysis.py > cg_analysis_$DATE_SHORT.txt
cat cg_analysis_$DATE_SHORT.txt
echo "CauseGraph: finished additional python scripts"
echo "CauseGraph: dump processed: $(date --utc +%Y%m%dT%H:%M:%S)"
# arangoimport --file "nodes.tsv" --type tsv --collection "items" --create-collection true
# arangoimport --file "relationships.tsv" --type tsv --collection "relations" --from-collection-prefix "items" --to-collection-prefix "items" --create-collection true --create-collection-type edge
# echo "CauseGraph: ArangoDB import complete: $(date --utc +%Y%m%dT%H:%M:%S)"
# nodejs --max_old_space_size=16384 makengraph.js
# ./fix_labels.py
# mkdir $DATE_SHORT
# cp data/positions.bin $DATE_SHORT
# cp links.bin $DATE_SHORT
# cp meta.json $DATE_SHORT
# cp newlabels.json $DATE_SHORT/labels.json
cd ../
#./update_notify.py
