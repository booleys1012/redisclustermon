# -*- coding: utf-8 -*-
from pyrcm.models.message import Message

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
This module houses the singleton Flask application wrapper class.
"""
import logging
import os
import threading

from flask import Flask, request
from flask_restful import Api
from flask_socketio import SocketIO, emit

from pyrcm.worker.rcworker import kickstart_rc_worker
from pyrcm.configmediator import ConfigMediator
from pyrcm.terminal.commandmediator import CmdMediator
from pyrcm.worker.summaryqueue import SummaryQueue


class _RcmFlaskAppInstance(object):
    """Core management class for Rcm Application
    
    Attributes:
        STATIC_FOLDER (str): path which the flask application hosts staticall
    """
    # assumes you are running from 'bin'
    STATIC_FOLDER = "/app/static"

    def __init__(self):
        static_folder = os.environ.get('STATIC_FOLDER', self.STATIC_FOLDER)
        
        self.port = int(os.environ.get('FLASK_PORT', 80))
        print 'hosting static dir {}'.format(static_folder)
        try:
            logging.info( 'hosting static dir {}'.format(static_folder) )
        except:
            print 'error'
        self.app = Flask(__name__,
                         static_folder=static_folder,
                         static_url_path='')
        self.api = Api(self.app)
        self.socketio = SocketIO(self.app)
        self.summaryq = SummaryQueue()
        self.clients = {}
        self.logger = logging.getLogger('app')
        self.running = True

    def add_client(self, c):
        """adds client from registry"""
        self.clients[c] = None

    def remove_client(self, c):
        """remove client from registry"""
        self.clients.pop(c)

    def get_config_mediator(self):
        """return a ConfigMediator which wraps the flask config"""
        return ConfigMediator()

    def _load_config(self):
        """loads the flask config file into the app
        
        this is deprecated -- switching to os.environ
        so user can drive the configuration into a 
        docker container
        
        """
        pass

    def _register_resources(self):
        """adds flask_restful resources to the application"""
        from pyrcm.flaskrcm.resources.ping import Ping
        self.api.add_resource(Ping, '/ping')

    def _start_worker(self):
        """spawns the thread which manages the cluster summary delivery"""
        self.workerthread = threading.Thread(
            name='worker_thread', target=kickstart_rc_worker, args=[self, ])
        self.workerthread.setDaemon(True)
        self.workerthread.start()

    def _socketio_on_connect(self, request):
        self.logger.info('client connected: {}'.format(request.sid))
        """handler method for socketio client connect event
        
        Args:
            request: the flask request object
        """
        self.add_client(request.sid)
        
        #send the command list
        cmdlistcontent = CmdMediator.get_commandlist()
        cmdlistmsg     = Message.buildClusterCommandList(cmdlistcontent)
        emit('message', cmdlistmsg.to_dict())
        
        #send summary history
        for m in self.summaryq.each_message():
            emit('message', m)

    def _socketio_on_disconnect(self, request):
        """handler method for socketio client disconnect event
        
        Args:
            request: the flask request object
        """
        self.logger.info('client disconnected: {}'.format(request.sid))
        self.remove_client(request.sid)

    def _socketio_on_message(self, request, message):
        """handler method for socketio `message` receipt
        
        Args:
            message (Message): the received Message from socketio
        """
        self.logger.info('{} ==> {}'.format(request.sid, message))

        rc = self.get_config_mediator().get_rc_client()
        response_message = CmdMediator(rc, message['content']).process()
        emit('message', response_message.to_dict())

    def prepare(self, run=True):
        """calls all initialization methods for underlying systems
        
        Args:
            run (bool): run the socketio main loop
        """
        self._load_config()
        self._register_resources()
        self._register_socketio_handlers()
        self._start_worker()
        try:
            if run:
                self.socketio.run(self.app, use_reloader=False,
                                  host='0.0.0.0',
                                  port=self.port)
        finally:
            self.running = False

    def _register_socketio_handlers(self):
        """connects the socketio handlers to classmethods within `self`"""

        @self.socketio.on('connect')
        def on_connect(): self._socketio_on_connect(request)

        @self.socketio.on('disconnect')
        def on_disconnect(): self._socketio_on_disconnect(request)

        @self.socketio.on('message')
        def on_message(message): self._socketio_on_message(request, message)


class RcmFlaskApp(object):
    """a singleton getter for the underlying core application class"""
    
    instance = None

    def __new__(cls):
        """the singleton getter method"""
        if not cls.instance:
            cls.instance = _RcmFlaskAppInstance()
        return cls.instance
