#!/bin/bash

echo "CauseGraph: starting Wikidata dump download: $(date --utc +%Y%m%dT%H:%M:%S)"
# the .gz is 50% larger than the .bz2, but it's ready sooner and unzips faster
# download to /tmp; make this tmpfs for even faster decompression
wget -N -P /tmp/ https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.gz
echo "CauseGraph: dump downloaded: $(date --utc +%Y%m%dT%H:%M:%S)"
zcat /tmp/latest-all.json.gz > latest-all.json
echo "CauseGraph: dump decompressed: $(date --utc +%Y%m%dT%H:%M:%S)"
WORKSPACE="workspace-$(date --utc +%Y%m%dT%H:%M:%S)"
mkdir -p $WORKSPACE
cp wd2cg.py $WORKSPACE
cp wd_constants.py $WORKSPACE
cp makengraph.js $WORKSPACE
cp fix_labels.py $WORKSPACE
cd $WORKSPACE
pypy wd2cg.py ../latest-all.json
echo "CauseGraph: dump processed: $(date --utc +%Y%m%dT%H:%M:%S)"
# DB_DIR="cg-$(date +%Y%m%d).db"
# mkdir $DB_DIR
# neo4j-import --into $DB_DIR --nodes nodes.tsv --relationships relationships.tsv --delimiter TAB --quote \|
# echo "CauseGraph: neo4j import complete: $(date --utc +%Y%m%dT%H:%M:%S)"
nodejs --max_old_space_size=16384 makengraph.js
pypy fix_labels.py
DATE_SHORT="$(date +%Y%m%d)"
mkdir $DATE_SHORT
cp data/positions.bin $DATE_SHORT
cp links.bin $DATE_SHORT
cp meta.json $DATE_SHORT
cp newlabels.json $DATE_SHORT/labels.json
cd ../
./update_notify.py
