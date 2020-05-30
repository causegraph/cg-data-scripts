#!/bin/bash

echo "CauseGraph: starting Wikidata dump download: $(date --utc +%Y%m%dT%H:%M:%S)"
# the .gz is 50% larger than the .bz2, but it's ready sooner and unzips faster
wget --no-if-modified-since -N https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.gz
echo "CauseGraph: dump downloaded: $(date --utc +%Y%m%dT%H:%M:%S)"
gunzip -k latest-all.json.gz
echo "CauseGraph: dump decompressed: $(date --utc +%Y%m%dT%H:%M:%S)"
WORKSPACE="workspace-$(date --utc +%Y%m%dT%H:%M:%S)"
mkdir -p $WORKSPACE
cp wd2cg.py $WORKSPACE
cp wd_constants.py $WORKSPACE
cp makengraph.js $WORKSPACE
cp fix_labels.py $WORKSPACE
cp filter.json $WORKSPACE
cd $WORKSPACE
./wd2cg.py ../latest-all.json
echo "CauseGraph: dump processed: $(date --utc +%Y%m%dT%H:%M:%S)"
# arangoimp --file "nodes.tsv" --type tsv --collection "items" --create-collection true
# arangoimp --file "relationships.tsv" --type tsv --collection "relations" --from-collection-prefix "items" --to-collection-prefix "items" --create-collection true --create-collection-type edge
# echo "CauseGraph: ArangoDB import complete: $(date --utc +%Y%m%dT%H:%M:%S)"
nodejs --max_old_space_size=16384 makengraph.js
./fix_labels.py
DATE_SHORT="$(date +%Y%m%d)"
mkdir $DATE_SHORT
cp data/positions.bin $DATE_SHORT
cp links.bin $DATE_SHORT
cp meta.json $DATE_SHORT
cp newlabels.json $DATE_SHORT/labels.json
cd ../
./update_notify.py
