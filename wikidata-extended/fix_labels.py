#!/usr/bin/env python3

import json

f = open('labels.json', 'r')
graphlabels = json.loads(f.read())
f.close()

f = open('wd_labels.json', 'r')
wd_labels = json.loads(f.read())
f.close()

newlabels = []

for label in graphlabels:
    if label in wd_labels:
        newlabels.append(' '.join([wd_labels[label], '-', label]))
    else:
        newlabels.append(label)

with open('newlabels.json', 'w') as outfile:
    outfile.write(json.dumps(newlabels, indent=True))
