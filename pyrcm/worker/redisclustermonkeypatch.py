# -*- coding: utf-8 -*-

# MIT License
#
# Copyright (c) 2018 Justin Bewley Lo (justinbewley.com)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
"""
a monkey patch provider for the issues caused by the latest version
of Redis conflicting with the current version of redis-cluster-py
"""

############################################################
# MONKEY PATCH REDIS CLIENT HERE
############################################################
from redis._compat import basestring, nativestr
import itertools


class Patch(object):

    @staticmethod
    def ranges(i):
        for a, b in itertools.groupby(enumerate(i), lambda (x, y): y - x):
            b = list(b)
            yield b[0][1], b[-1][1]

    @classmethod
    def parse_cluster_nodes(cls, resp, **options):
        """
        @see: http://redis.io/commands/cluster-nodes  # string
        @see: http://redis.io/commands/cluster-slaves # list of string
        """
        resp = nativestr(resp)
        current_host = options.get('current_host', '')

        def parse_slots(s):
            slots, migrations = [], []
            for r in s.split(' '):
                if '->-' in r:
                    slot_id, dst_node_id = r[1:-1].split('->-', 1)
                    migrations.append({
                        'slot': int(slot_id),
                        'node_id': dst_node_id,
                        'state': 'migrating'
                    })
                elif '-<-' in r:
                    slot_id, src_node_id = r[1:-1].split('-<-', 1)
                    migrations.append({
                        'slot': int(slot_id),
                        'node_id': src_node_id,
                        'state': 'importing'
                    })
                elif '-' in r:
                    start, end = r.split('-')
                    slots.extend(range(int(start), int(end) + 1))
                else:
                    slots.append(int(r))

            return slots, migrations

        if isinstance(resp, basestring):
            resp = resp.splitlines()

        nodes = []
        for line in resp:
            parts = line.split(' ', 8)
            self_id, addr, flags, master_id, ping_sent, \
                pong_recv, config_epoch, link_state = parts[:8]

            host, ports = addr.rsplit(':', 1)
            port, _, cluster_port = ports.partition('@')

            node = {
                'id': self_id,
                'host': host or current_host,
                'port': int(port),
                'cluster-bus-port': int(cluster_port) if cluster_port else 10000 + int(port),
                'flags': tuple(flags.split(',')),
                'master': master_id if master_id != '-' else None,
                'ping-sent': int(ping_sent),
                'pong-recv': int(pong_recv),
                'link-state': link_state,
                'slots': [],
                'migrations': [],
            }

            if len(parts) >= 9:
                slots, migrations = parse_slots(parts[8])
                node['slots'], node['migrations'] = tuple(slots), migrations
                node['slots'] = list(cls.ranges(node['slots']))

            #print node['slots']
            nodes.append(node)

        return nodes
