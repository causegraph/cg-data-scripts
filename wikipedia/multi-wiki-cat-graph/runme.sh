#wget --no-if-modified-since -N https://dumps.wikimedia.org/wikidatawiki/entities/latest-all.json.gz
#gunzip -k latest-all.json.gz
#pypy3 process_wd.py

for i in en de fr ru it es pl ja pt ar nl sv uk ca tr no fi id vi zh he
do
  wget --no-if-modified-since -N https://dumps.wikimedia.org/${i}wiki/latest/${i}wiki-latest-pages-articles-multistream.xml.bz2
  bunzip2 -k ${i}wiki-latest-pages-articles-multistream.xml.bz2
  echo "decompression complete"
  python3 process_wp.py ${i}
  rm ${i}wiki-latest-pages-articles-multistream.xml
done

pypy3 combine.py
