#!/bin/bash

remote_file="https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.gz"
local_file="/tmp/latest-all.json.gz"

if [ -e $local_file ]
then
    # run cg.sh *if there is a newer file*
    modified=$(curl --silent --head $remote_file | \
                 awk '/^Last-Modified/{print $0}' | \
                 sed 's/^Last-Modified: //')
    remote_ctime=$(date --date="$modified" +%s)
    local_ctime=$(stat -c %z "$local_file")
    local_ctime=$(date --date="$local_ctime" +%s)

    [ $local_ctime -lt $remote_ctime ] && ./cg.sh
else
    # we need to download the file
    ./cg.sh
fi
