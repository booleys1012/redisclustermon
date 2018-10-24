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

from pyrcm.models.message import Message
from pyrcm.terminal.commandresponse import CmdResponse
from pyrcm.terminal.rediscmd_get import RedisClusterCmd_Get
from pyrcm.terminal.rediscmd_noop import RedisClusterCmd_Noop
from pyrcm.terminal.rediscmd_scaniter import RedisClusterCmd_ScanIter
from pyrcm.terminal.rediscmd_hget import RedisClusterCmd_Hget
from pyrcm.terminal.rediscmd_hgetall import RedisClusterCmd_Hgetall
from pyrcm.terminal.rediscmd_exists import RedisClusterCmd_Exists
from pyrcm.terminal.rediscmd_del import RedisClusterCmd_Del


class CmdMediator(object):
    CmdList = [RedisClusterCmd_Get,
               RedisClusterCmd_Hget,
               RedisClusterCmd_Hgetall,
               RedisClusterCmd_ScanIter,
               RedisClusterCmd_Exists,
               RedisClusterCmd_Del,
               ]

    CmdMap = {kls.CMDNAME: kls for kls in CmdList}

    def __init__(self, rc_client, cmd):
        self.rc_client = rc_client
        self.cmd = self.clean_cmd(cmd)
    
    @classmethod
    def get_commandlist(cls):
        cmdlist = {}
        for c in cls.CmdList:
            cmdlist[c.CMDNAME] = c.CMDDETAILS
        return cmdlist
    
    @staticmethod
    def clean_cmd(cmd):
        result = [x.strip() for x in cmd.strip().split()]
        result = [x for x in result if x]
        return result

    def process(self):
        cmdclass = self.CmdMap.get(self.cmd[0], RedisClusterCmd_Noop)
        resp = cmdclass(self.rc_client, self.cmd).get_response()
        return Message.buildTerminalResponse(resp.as_dict())
