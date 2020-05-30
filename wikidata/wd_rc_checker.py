import json
from sseclient import SSEClient as EventSource

import wd_constants

url = "https://stream.wikimedia.org/v2/stream/recentchange"
wiki = 'wikidatawiki'

# TODO put in wd_constants
# TODO figure out how to handle dates/times?
#      need to parse e.g. "1882", "8 December 2001", "1920s"
#      and how those are positioned at the end of the comment
all_rels = frozenset(list(wd_constants.cg_rels.keys()) +
                     list(wd_constants.nested_time_rels.keys()))

readable_names = {
    'wbcreateclaim': 'claim created:',
    # 'wbeditentity': 'item created:', # maybe don't need this
    'wbsetclaim-create': 'claim set:',
    'wbsetclaim-update': 'claim updated:',
    'wbsetclaimvalue': 'claim value set:',
    'wbremoveclaims': 'claims removed:'
}


def process_comment(comment):
    # TODO cleaner implementation, maybe regex?
    spl = comment.split()
    wb_op, wd_prop, wd_val = spl[1], spl[3].strip(u'[]:'), spl[4].strip(u'[],')
    return wb_op, wd_prop, wd_val


for event in EventSource(url):
    if event.event == 'message':
        try:
            change = json.loads(event.data)
        except ValueError:
            continue
        if change['wiki'] == wiki and 'comment' in change:
            # print('{user} edited {title}:'.format(**change))
            try:
                op, prop, val = process_comment(change['comment'])
                if 'Property:' in prop:
                    prop = prop[9:]
                for k in readable_names:
                    if k in op and prop in all_rels: #.union(wd_constants.all_times):
                        print(change['meta']['dt'], k, change['meta']['uri'], prop, val)
                    if k in op and prop in wd_constants.all_times:
                        print(change['meta']['dt'], k, change['meta']['uri'], change['comment'])
            except:
                pass
                # print('ERROR on {title}: {comment}'.format(**change))

            # print(json.dumps(change, indent=4))
