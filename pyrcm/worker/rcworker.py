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
The methods and modules related to running the RCM background thread.

The thread uses a StrictRedisCluster to gather information on the redis cluster
and deliver them through socketio to clients

The thread entry method is kickstart_rc_worker
"""

from datetime import datetime
import json
import gevent
import logging
import time

from pyrcm.models.message import Message


class ClusterSummaryNode(object):
    """representation of the data pertaining to a single Redis node"""
    
    INFO_FIELDS = [
        'aof_enabled',
        'cluster_size',
        'cluster_state',
        'cluster_slots_fail',
        'cluster_slots_ok',
        'connected_clients',
        'connected_slaves',
        'instantaneous_ops_per_sec',
        'master_host',
        'master_port',
        'uptime_in_seconds',
        'used_memory',
        'used_memory_rss',
        'total_system_memory',
        'db0'
    ]

    TIME_STAT_INFO_FIELDS = {
        'used_memory': lambda info: info['used_memory'],
        'used_memory_rss': lambda info: info['used_memory_rss'],
    }

    def __init__(self, hostport, info=None, node=None, slaves=None):
        self.hostport = hostport
        self.info = info
        self.node = node
        self.slaves = slaves if slaves else []

    def info_optimized(self):
        """filters the `info` object for bandwidth limitation"""
        return {
            k: self.info.get(k) for k in self.INFO_FIELDS
        }

    def node_optimized(self):
        """placeholder for optimizing the `node` data object"""
        return {
            k: v for k, v in self.node.iteritems()
        }

    def slaveto(self, id_to_hostport_map):
        """gets the node id of this node's master, if applicable"""
        result = None
        try:
            result = id_to_hostport_map[self.node['master']]
        except:
            pass
        return result

    def to_dict(self):
        """converts the summary into a dictionary for socketio delivery"""
        nodesummary = {
            'id': self.hostport,
            'info': self.info_optimized(),
            'node': self.node_optimized(),
            'slaves': [x.to_dict() for x in self.slaves],
            'timestats': {k: v(self.info) for k, v in self.TIME_STAT_INFO_FIELDS.iteritems()}
        }
        return nodesummary

    def __str__(self):
        return '{} slaves: {}'.format(self.hostport, [x.hostport for x in self.slaves])


class ClusterSummary(object):

    LOOP_PREVENTION = 10

    def __init__(self, cluster_nodes, cluster_info):
        self.keys = cluster_nodes.keys()
        self.keys += cluster_info.keys()
        self.keys = list(set(self.keys))

        self.idmap = dict([(x['id'],
                            '{}:{}'.format(x['host'], x['port']))
                           for x in cluster_nodes.values()])

        self.summary = {k: ClusterSummaryNode(k) for k in self.keys}
        for hostport, node in cluster_nodes.iteritems():
            self.summary[hostport].node = node
        for hostport, info in cluster_info.iteritems():
            self.summary[hostport].info = info

        loop_number = 0
        while self.reorg(loop_number):
            loop_number += 1

    def reorg(self, loop_number):
        """reorganizes the summary object so that slaves at the same level as 
        their master are placed within the `slave` field of that master"""
        
        if loop_number >= self.LOOP_PREVENTION:
            raise Exception(
                'reorg of cluster summary structure detected bad loop')

        reorg_map = {k: v.slaveto(self.idmap)
                     for k, v in self.summary.iteritems()}
        reorg_map = {k: v for k, v in reorg_map.iteritems() if v}

        for slavehostport, masterhostport in reorg_map.iteritems():

            #print 'migrating {} to {}'.format(slavehostport, masterhostport)
            node = self.summary.pop(slavehostport)
            self.summary[masterhostport].slaves.append(node)
        return len(reorg_map) > 0

    def to_dict(self):
        """converts this object to a JSON-friendly dictionary"""
        return {
            k: v.to_dict() for k, v in self.summary.iteritems()
        }

    def __str__(self):
        r = ''
        for hostport, node in self.summary.iteritems():
            r += '\n{}: {}'.format(hostport, node)
        return r


class ClusterSummarizer(object):

    @classmethod
    def get_summary(cls, rc_client):
        """polls the redis client for updated information and builds and
        returns the summary built from those updates
        """
        cluster_nodes = rc_client.cluster_nodes()
        cluster_nodes = dict(
            [('{}:{}'.format(x['host'], x['port']), x) for x in cluster_nodes])
        cluster_info = rc_client.cluster_info()
        info = rc_client.info()

        for k, v in cluster_info.iteritems():
            try:
                v.update(info[k])
            except:
                logging.exception("info is unavailable for node[{}]".format(k))

        cluster_summary = ClusterSummary(cluster_nodes, cluster_info)
        return cluster_summary.to_dict()


class RcWorker(object):
    """Main thread processing class for periodically loading redis cluster
    updates and delivering those updates to the socketio
    """
    def __init__(self, app):
        self.app   = app
        self.sleep = app.get_config_mediator().RCM_REDIS_SUMMARY_DELAY
        self.refresh_rc_client()

    def refresh_rc_client(self):
        """builds a new StrictRedisCluster instance"""
        self.rc_client = self.app.get_config_mediator().get_rc_client()

    def emit_cluster_summary(self, message):
        """deliver a `Message` object which represents a cluster summary 
        to the socketio"""
        self.app.socketio.emit('message', message, broadcast=True)
        gevent.sleep(0)

    def run_forever(self):
        """main processing loop for the worker thread"""
        while self.app.running:
            try:
                csummary = ClusterSummarizer.get_summary(self.rc_client)

                messagecontent = {
                    'unixtime': time.mktime(datetime.now().timetuple()),
                    'csummary': csummary
                }
                m = Message.buildClusterSummary(
                    json.dumps(messagecontent)).to_dict()
                self.emit_cluster_summary(m)
                self.app.summaryq.add(m)
            except:
                logging.exception("failure in main loop")
                self.refresh_rc_client()
            finally:
                gevent.sleep(self.sleep)


def kickstart_rc_worker(app):
    """entry point for the worker thread"""
    try:
        logging.info('starting worker...')
        RcWorker(app).run_forever()
    finally:
        logging.info('terminating...')

