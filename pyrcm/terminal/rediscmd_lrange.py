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

from pyrcm.terminal.rediscmd import RedisClusterCmd


class RedisClusterCmd_Lrange(RedisClusterCmd):

    CMDNAME = 'LRANGE'

    CMDDETAILS = {
        'read_or_write': 'read',
        'description':   'returns elements of a list',
        'example': '{} [key] [stop] [start]'.format(CMDNAME)
    }
    def __init__(self, rc_client, args):
        super(RedisClusterCmd_Lrange, self).__init__(rc_client, args)

    def get_args_error(self):
        resp = None
        if len(self.args) != 4:
            resp = "invalid number of arguments"
        return resp

    def runcmd(self):
        return self.rc_client.lrange(self.args[1], self.args[2], self.args[3])
