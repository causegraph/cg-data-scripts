These steps are basically the process used to transform DBpedia data into the best current implementation of CauseGraph ([Causalaxies](https://causegraph.github.io/causalaxies)).  This documentation may not be perfect, and the process itself certainly isn't.

To go from DBpedia's data to a graph of influence relationships:
1. Grab DBpedia data: `wget http://downloads.dbpedia.org/2015-04/core-i18n/en/mappingbased-properties_en.nt.bz2`
2. Get the part we're interested in: `bzgrep influenced mappingbased_properties_en.nt > dbpedia_influences.nt`
3. Run a Python script to turn this into the graph that we want: `python make_cgproto.py`

We want to use time information to inform our layout, so we generate a JSON file with birth years, where available:
1. Get the part we're interested in: `bzgrep birthYear mappingbased-properties_en.nt.bz2 > dbpedia_birth_years.nt`
2. Run `ngraphwithdates.js` to create and save an ngraph.graph structure that includes the date information.

This documentation is not yet complete.