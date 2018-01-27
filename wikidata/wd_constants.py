from __future__ import absolute_import, division, print_function

# language fallback chain; get labels in the first language that works
# the goal being to provide readable labels
lang_order = ('en', 'de', 'fr', 'es', 'it', 'pl', 'pt', 'nl', 'sv', 'no', 'fi',
              'ro')

cg_rels = {
    'P737': 'influenced by',
    'P941': 'inspired by',
    'P2675': 'reply to',
    'P144': 'based on',
    'P828': 'has cause',
    'P1542': 'cause of',
    'P1478': 'has immediate cause',
    'P1536': 'immediate cause of',
    'P1479': 'has contributing factor',
    'P1537': 'contributing factor of',
    'P22': 'father',
    'P25': 'mother',
    'P40': 'child',
    'P184': 'doctoral advisor',
    'P185': 'doctoral student',
    'P1066': 'student of',
    'P802': 'student'
}

# TODO these may have nested date information, so look at them
nested_time_rels = {
    'P348': 'software version',
    'P106': 'occupation',
    'P108': 'employer',
    'P69': 'educated at',
    'P26': 'spouse',
    'P176': 'manufacturer',
    'P449': 'original network'
}

# other relationships being considered, not yet in CG
other_rels = {
    'P2860': 'cites',
    'P807': 'separated from',
    'P112': 'founded by',
    'P170': 'creator',  # TODO: add subproperties
}

# if a statement using one of these doesn't have a date on either end,
# then it's probably something like "ethanol cause of ethanol exposure",
# which isn't suitable for CauseGraph.  TODO: Filter that stuff.
likely_nonspecific = frozenset(
    ['P828', 'P1542', 'P1478', 'P1536', 'P1479', 'P1537'])

# these aren't that great, would need lots of filtering
# 'P509': 'cause of death', 'P770': 'cause of destruction',

# there's also P523 and P524 for 'temporal range' for e.g. dinosaurs

# TODO get subproperties for times below; you're still missing some
# TODO use earliest and latest when present with an unknown date

starts = {
    'P580': 'start time',
    'P571': 'inception',
    'P569': 'date of birth',
    'P575': 'time of discovery',
    'P1191': 'first performance',
    'P577': 'publication date',
    'P2031': 'work period (start)',
    'P1619': 'date of official opening',
    'P1319': 'earliest date',
    'P729': 'service entry'
}

ends = {
    'P582': 'end time',
    'P576': 'dissolved, abolished or demolished',
    'P570': 'date of death',
    'P2032': 'work period (end)',
    'P2669': 'discontinued date',
    'P1326': 'latest date',
    'P730': 'service retirement'
}

others = {
    'P793': 'significant event',
    'P585': 'point in time',
    'P1317': 'floruit'
}

all_times = frozenset(list(starts.keys()) +
                      list(ends.keys()) +
                      list(others.keys()))

times_plus_nested = frozenset(list(starts.keys()) +
                              list(ends.keys()) +
                              list(others.keys()) +
                              list(nested_time_rels.keys()))

# these inverse relationships are present in Wikidata
original_inverses = {
    'P22': 'P40',  # father/mother more specific
    'P25': 'P40',
    'P828': 'P1542',
    # 'P828': 'P1536',  # both listed as inverses? not sure it makes sense
    'P184': 'P185',
    'P1066': 'P802',
    'P1478': 'P1536',
    'P1479': 'P1537'
}

combined_inverses = {
    'P22': 'P40',  # "father of"
    'P25': 'P40',  # "mother of"
    'P737': 'P737i',  # "influenced"
    'P941': 'P941i',  # "inspired"
    'P2675': 'P2675i',  # "received reply"
    'P144': 'P144i',  # "basis of"
    'P828': 'P1542',
    'P184': 'P185',
    'P1066': 'P802',
    'P1478': 'P1536',
    'P1479': 'P1537'
}

fictional_properties = ('P1074')

# TODO remove this if filtering code works
do_not_show = frozenset([
    'Q166231',  # infection
    'Q21396183',  # arsenic pentoxide exposure
    'Q16943283',  # Rape of Europa
    'Q21175052',  # phosphine exposure
    'Q21504975',  # lewisite exposure
    'Q12147416',  # drug resistance
    'Q21167939',  # benzene exposure
    'Q408089',  # mercury poisoning
    'Q1784308',  # Judgement of Paris
    'Q12090',  # cholera
    'Q21174755',  # hydrogen fluoride exposure
    'Q21175308',  # sodium cyanide exposure
    'Q21513721',  # mechlorethamine exposure
    'Q21973551',  # chemical
    'Q21167853',  # chemical
    'Q21175069',  # chem
    'Q21514015',  # chem
    'Q21174754',  # chem
    'Q21173555',  # chem
    'Q21174113',  # chem
    'Q21402492',  # chem
    'Q21174897',  # chem
    'Q21175054',  # chem
    'Q21506740',  # chem
    'Q47912',  # lung cancer
    'Q11663',  # weather; yes, just weather, in general
    'Q3196',  # fire
    'Q173022',  # bronchitis
    'Q5421292',  # exploding animal
    'Q1366544',  # beached whale
])

# these came into existence at a certain time that can be pointed to
# (generally ~2000 years ago), but they don't have date info in Wikidata now
unsure = [
    'Q9309699',  # Madonna and child, artistic theme
    'Q370665',  # Sacred conversation, artistic theme
    'Q34726',  # Ancient Greek mythology
    'Q154326',  # Annunciation, holiday and artistic theme
    'Q9184',  # Book of Genesis
    'Q5989722',  # Penitent Magdalene, yet another Christian artistic theme
    'Q488841',  # Adoration of the Magi
    'Q16930210',  # Susanna and the Elders
    'Q2509393',  # Saint George and the Dragon
    'Q633534',  # Death of Cleopatra - artistic theme based on actual event
    'Q19786',  # Old Testament
    'Q18813',  # New Testament
    'Q1029715',  # Adoration of the shepherds, Christian artistic theme
    'Q15914389',  # ancient Chinese monarch, precise date of birth not known
    'Q51628',  # Nativity of Jesus
    'Q7885664',  # Dance of the Seven Veils
    'Q42040',  # Book of Revelation
    'Q1004401',  # Bridal theology, yet another Christian artistic theme
    'Q837143',  # Flight into Egypt, "biblical episode"
    'Q202129',  # Book of Judith
    'Q910606',  # music of Brittany; exclude as too general?
]

todo = [
    'Q735117',  # a reminder to use earliest/latest in the case of unknown date
    'Q462',  # Star Wars - need some sort of date, but item has none
    'Q1092',  # Start Trek - same thing
    'Q1233460'  # labors of Hercules: exclude all ancient Greek mythology?
]
