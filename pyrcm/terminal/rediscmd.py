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

import logging
from pyrcm.terminal.commandresponse import CmdResponse


class RedisClusterCmd(object):

    CMDNAME = None
    CMDDETAILS = {
        'read_or_write': None,
        'description':   None,
        'example':       None
    }
    def __init__(self, rc_client, args):
        self.rc_client = rc_client
        self.args = args

    def get_args_error(self):
        raise NotImplementedError(self.CMDNAME)

    def runcmd(self):
        raise NotImplementedError(self.CMDNAME)

    def get_response(self):
        cmdresponse = CmdResponse(self.CMDNAME)

        args_error = self.get_args_error()
        if args_error:
            cmdresponse.set_data(args_error, is_error=True)
        else:
            try:
                cmdresponse.set_data(self.runcmd())
            except:
                cmdresponse.set_data('unexpected exception', is_error=True)

        return cmdresponse
