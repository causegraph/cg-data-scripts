dates_to_filter = frozenset(open('filter.txt', 'r').read().split('\n'))
def keep(statement, items_to_filter=dates_to_filter):
    splitup = statement.strip().split(' | ')
    if splitup[0] not in items_to_filter and splitup[1] not in items_to_filter:
        return True
    else:
        return False

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
     open('wd_missing.txt', 'w') as wd_missing, \
     open('wd_missing_filtered.txt', 'w') as wd_missing_filtered:
    statements = frozenset(wd_file.readlines())
    print('number of statements from Wikidata:', len(statements))
    missing = intersection - statements
    print('number of intersection items missing from Wikidata:', len(missing))
    wd_missing.writelines(missing)
    missing_filtered = [item for item in missing if keep(item)]
    print('previous with selected dates filtered:', len(missing_filtered))
    wd_missing_filtered.writelines(missing_filtered)
