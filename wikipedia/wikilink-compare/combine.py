langs = ('en', 'de', 'fr', 'ru', 'it', 'es', 'pl', 'ja', 'pt', 'ar', 'nl',
         'sv', 'uk', 'ca', 'tr', 'no', 'fi', 'id', 'vi', 'zh', 'he')
langsets = []
for lang in langs:
    try:
        langsets.append(frozenset(open(lang + 'wikilinks.txt').readlines()))
    except FileNotFoundError:
        print(lang + 'wikilinks.txt file not found')

# TODO get rid of newlines and stuff

intersection = frozenset.intersection(*langsets)

print('number of common links between all languages:', len(intersection))

with open('intersection-combined.txt', 'w') as outfile:
    outfile.writelines(intersection)

# let's try this... eek
union = frozenset.union(*langsets)

print('number of unique links between all languages:', len(union))

with open('union-combined.txt', 'w') as outfile:
    outfile.writelines(union)

print('testing intersection - union:', len(intersection - union))

del union

with open('statements.txt', 'r') as wd_file, \
     open('filter.txt', 'r') as filterfile, \
     open('wd_missing.txt', 'w') as wd_missing:
    filter = frozenset(filterfile.read().split('\n'))
    statements = frozenset(wd_file.readlines())
    missing = intersection - statements
    # TODO finish the following line
    # filtered = {item for item in missing if }
    print('number of intersection items missing from Wikidata:', len(missing))
    wd_missing.writelines(missing)
