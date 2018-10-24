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

from rediscluster import StrictRedisCluster
from pyrcm.worker.redisclustermonkeypatch import Patch
import os


class ConfigMediator(object):
    """A mediator class that grants helper methods to access the app config"
        
    Args:
        appconfig (flask.Flask.config): the application config
    """
    ConfigDict = {}
    
    def __init__(self):
        pass

    @property
    def RCM_REDIS_STARTUP_NODES(self):
        return os.environ['RCM_REDIS_STARTUP_NODES']

    @property
    def RCM_REDIS_SUMMARY_DELAY(self): 
        return int(os.environ.get('RCM_REDIS_SUMMARY_DELAY', 5))

    def get_rc_client(self):
        """builds a StrictRedisCluster instance based on configuration
        
        Returns:
            StrictRedisCluster
        """
        startup_nodes = []
        for hostport in self.RCM_REDIS_STARTUP_NODES.split(','):
            host, port = hostport.split(':')
            startup_nodes.append({'host': host, 'port': port})

        client = StrictRedisCluster(startup_nodes=startup_nodes)
        client.set_response_callback('CLUSTER NODES', Patch.parse_cluster_nodes)
        return client
