#!/usr/bin/env python3

import json
import time
import multiprocessing as mp
import networkx as nx

from wd2cg import make_qid_nx_graph
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

def check_recent_changes(q):
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
                            qid = change['meta']['uri'].rsplit('/', 1)[1]
                            q.put((k, qid, prop, val))
                        if k in op and prop in wd_constants.all_times:
                            print(change['meta']['dt'], k, change['meta']['uri'], change['comment'])
                except:
                    pass
                    # print('ERROR on {title}: {comment}'.format(**change))

                # print(json.dumps(change, indent=4))

def print_graph_status(g):
    nn = g.number_of_nodes()
    ne = g.number_of_edges()
    print('UPDATE: graph now has %s nodes and %s edges' % (nn, ne))


def add_wd_edge(graph, src, typ, dst):
    pass

if __name__ == '__main__':
    years = json.loads(open('wd_years.json', 'r').read())

    g = nx.MultiDiGraph()

    try:
        with open('statements_final.txt', 'r') as statements:
            g = make_qid_nx_graph(statements, years)
    except FileNotFoundError:
        print('ERROR: statements file not found; starting with empty graph')

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
                op, src, typ, dst = line.strip().split()
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

    # p.join()
