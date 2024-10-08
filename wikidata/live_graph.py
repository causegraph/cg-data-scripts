#!/usr/bin/env python3

import json
import time
import multiprocessing as mp
import networkx as nx

from wd2cg import make_qid_nx_graph
from pywikibot.comms.eventstreams import EventStreams

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
    'wbeditentity': 'item created:', # maybe don't need this
    'wbsetclaim-create': 'claim set:',
    'wbsetclaim-update': 'claim updated:',
    'wbsetclaimvalue': 'claim value set:',
    'wbremoveclaims': 'claims removed:'
}


wd_url = 'https://wikidata.org/wiki/'
skipchars = len(wd_url)
# the API URL to get detailed info on multiple items from Wikidata
url_base = 'https://www.wikidata.org/w/api.php?action=wbgetentities&format=json&ids='
search_url_base = 'https://www.wikidata.org/w/api.php?action=wbsearchentities&format=json&search='
# the documented limit on how many items can be queried at once
query_limit = 50


def check_recent_changes(q):
    def get_entities(query_ids):
        print('&&&&& STARTING TO GET ENTITY')
        ids_joined = '|'.join(query_ids)
        print(url_base + ids_joined)
        req = urllib.request.Request(url_base + ids_joined)
        print('adding header...')
        req.add_header('User-Agent', 'LiveGraphChecker/0.1 (https://www.wikidata.org/wiki/User:Jamie7687)')
        # req.add_header('Accept-Encoding', 'gzip')
        #time.sleep(0.1)
        print('****** about to get result...', url_base + ids_joined)
        result = urllib.request.urlopen(req)
        print('result *******')
        print(result)
        result_json = json.loads(result.read())
        if result_json['success'] == 1:
            return result_json['entities']
        else:
            raise Exception('wbgetentities call failed')

    def process_comment(comment):
        # TODO cleaner implementation, maybe regex?
        spl = comment.split()
        wb_op, wd_prop, wd_val = spl[1], spl[3].strip(u'[]:'), spl[4].strip(u'[],')
        return wb_op, wd_prop, wd_val

    def out_of_order(qid):
        """check that begin/end times are in order"""
        print('**** checking order..... *****')
        # not sure about this
        has_start, has_end, has_other = False, False, False
        date_space = {}
        result = []
        entity = get_entities([qid])[qid]
        print('****ENTITY****')
        print(entity)
        if 'claims' in entity:
            print('claims in entity')
            claims = entity['claims']
            for c in claims:
                if c in wd_constants.starts:
                    print('starts')
                    for spec in claims[c]:
                        if 'time' in spec['mainsnak'].get('datavalue', {}).get(
                                'value', {}):
                            date = spec['mainsnak']['datavalue']['value']['time']
                            precision = spec['mainsnak']['datavalue']['value']['precision']
                            #result.append([claim, date, precision])
                            date_space['starts'][c] = (date, precision)
                elif c in wd_constants.ends:
                    print('ends')
                    for spec in claims[c]:
                        if 'time' in spec['mainsnak'].get('datavalue', {}).get(
                                'value', {}):
                            date = spec['mainsnak']['datavalue']['value']['time']
                            precision = spec['mainsnak']['datavalue']['value']['precision']
                            #result.append([claim, date, precision])
                            date_space['ends'][c] = (date, precision)
                elif c in wd_constants.others:
                    print('others')
                    for spec in claims[c]:
                        if 'time' in spec['mainsnak'].get('datavalue', {}).get(
                                'value', {}):
                            date = spec['mainsnak']['datavalue']['value']['time']
                            precision = spec['mainsnak']['datavalue']['value']['precision']
                            #result.append([claim, date, precision])
                            date_space['others'][c] = (date, precision)

            # need to make sure that starts come before others come before ends, generally
            #TODO finish this...
            if 'starts' in date_space:
                if 'ends' in date_space:
                    # check that starts come before ends
                    for s in date_space['starts']:
                        for e in date_space['ends']:
                            if not date_space['starts'][s][0] <= date_space['ends'][e][0]:
                                print('*******   !!!!GOT ONE!!!!    *******')
                                return True
                        for o in date_space['others']:
                            if not date_space['starts'][s][0] <= date_space['others'][o][0]:
                                print('*******   !!!!GOT ANOTHER!!!!    *******')
                                return True
                    return False
                elif 'others' in date_space:
                    # check that starts come before others?
                    for o in date_space['others']:
                        if not date_space['starts'][s][0] <= date_space['others'][o][0]:
                            print('*******   !!!!GOT ANOTHER!!!!    *******')
                            return True
                    return False
                else:
                    return False
            elif 'ends' in date_space:
                if 'others' in date_space:
                    # check that ends come after others
                    for e in date_space['ends']:
                        for o in date_space['others']:
                            if not date_space['ends'][e][0] <= date_space['others'][o][0]:
                                print('*******   !!!!GOT ANOTHER!!!!    *******')
                                return True
                    return False
            else:
                return False
        else:
            print('claims not found in entity?')





    stream = EventStreams(streams=['recentchange'])
    stream.register_filter(wiki='wikidatawiki', type='edit')

    for change in stream:
        try:
            op, prop, val = process_comment(change['comment'])
            if 'Property:' in prop:
                prop = prop[9:]
            for k in readable_names:
                if k in op and prop in all_rels:  # .union(wd_constants.all_times):
                    print(json.dumps(change, indent=2))
                    print(change['meta']['dt'], k, change['meta']['uri'], prop, val)
                    qid = change['meta']['uri'].rsplit('/', 1)[1]
                    q.put((k, qid, prop, val))
                if k in op and prop in wd_constants.all_times:
                    print(json.dumps(change, indent=2))
                    qid = change['meta']['uri'].rsplit('/', 1)[1]
                    print("@@@@ Checking out of order for", qid)
                    if out_of_order(qid):
                        print('***** SOMETHING IS OUT OF ORDER IN', qid)
                    print(change['meta']['dt'], k, change['meta']['uri'], change['comment'])
        except Exception:
            pass


def print_graph_status(g):
    nn = g.number_of_nodes()
    ne = g.number_of_edges()
    print('UPDATE: graph now has %s nodes and %s edges' % (nn, ne))


def add_wd_edge(graph, src, typ, dst):
    pass


if __name__ == '__main__':
    years = {}

    try:
        years = json.loads(open('wd_years.json', 'r').read())
    except FileNotFoundError:
        print('Years file not found; starting with empty years dict')

    g = nx.MultiDiGraph()

    try:
        with open('statements_final.txt', 'r') as statements:
            g = make_qid_nx_graph(statements, years)
    except FileNotFoundError:
        print('Statements file not found; starting with empty graph')

    print_graph_status(g)

    edges_added = 0
    just_added = False

    mp.set_start_method('spawn')
    q = mp.Queue()
    p = mp.Process(target=check_recent_changes, args=(q,))
    p.start()

    # TODO should I really just append?  When to start fresh?
    with open('graph_changes.txt', 'a+') as changes:
        edges_added_from_file = 0
        changes.seek(0)
        for line in changes.readlines():
            if not line.startswith('#'):
                try:
                    op, src, typ, dst = line.strip().split()
                except ValueError:
                    print('ValueError on line:', line)
                    continue
                if op in ('wbcreateclaim', 'wbsetclaim-create'):
                    if typ in wd_constants.cg_rels:
                        g.add_edge(src, dst, type=typ)
                        edges_added_from_file += 1
                    # should I notify for nested_time_rels? I guess not
                elif op == 'wbremoveclaims':
                    if g.has_edge(src, dst):
                        # TODO change the following line to work with MultiDiGraph edges
                        # i.e. g.get_edge_data()[0] - the 0 is for one of potentially multiple edges
                        # if g.get_edge_data(src, dst)[0]['type'] == typ:
                        # g.remove_edge(src,dst)
                        print('not removing edge of type %s from %s to %s' % (typ, src, dst))
                else:
                    print('IMPLEMENT handling for', op)
            else:
                print('adding', line[1:-1])
        print(edges_added_from_file, 'edges added from existing graph_changes file')
        print_graph_status(g)

        changes.write('#changes starting ' + time.ctime() + '\n')
        while True:
            if not q.empty():
                op, src, typ, dst = q.get()
                if op in ('wbcreateclaim', 'wbsetclaim-create'):
                    if typ in wd_constants.cg_rels:
                        g.add_edge(src, dst, type=typ)
                        just_added = True
                        edges_added += 1
                        changes.write(' '.join([op, src, typ, dst]) + '\n')
                        # changes.flush()
                    # should I notify for nested_time_rels? I guess not
                elif op == 'wbremoveclaims':
                    if g.has_edge(src, dst):
                        # TODO change the following line to work with MultiDiGraph edges
                        # i.e. g.get_edge_data()[0] - the 0 is for one of potentially multiple edges
                        # if g.get_edge_data(src, dst)[0]['type'] == typ:
                        # g.remove_edge(src,dst)
                        print('not removing edge of type %s from %s to %s' % (typ, src, dst))
                else:
                    print('IMPLEMENT handling for', op)
                # TODO choose a better condition here
                if edges_added > 0 and edges_added % 10 == 0 and just_added:
                    print_graph_status(g)
                    print(edges_added, 'edges added')
                    print('queue size is', q.qsize())
                    just_added = False
                    changes.flush()
            time.sleep(.2)
