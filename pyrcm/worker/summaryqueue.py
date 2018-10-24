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

"""a thread safe queue which contains historical summaries so that new 
frontent clients can start with some historical information"""

from contextlib import contextmanager
from threading import Lock


class SummaryQueue(object):
    """a thread-safe container of recent messages"""
    
    MAXELEMS = 100

    def __init__(self):
        self._mutex = Lock()
        self._messagequeue = []

    @contextmanager
    def _access(self):
        """protects the `_messagequeue` member"""
        self._mutex.acquire()
        yield
        self._mutex.release()

    def add(self, summary):
        """adds a summary to the queue
        
        Args:
            summary (Message): the message to store
        """
        with self._access():
            self._messagequeue.append(summary)
            if len(self._messagequeue) >= self.MAXELEMS:
                self._messagequeue = self._messagequeue[1:]

    def each_message(self):
        """a generator which iterates through the queue"""
        with self._access():
            for m in self._messagequeue:
                yield m
