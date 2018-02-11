from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')


def add_remote_mine(inp):
    if len(inp) != 2:
        console.log('[hive room-name] [remote-mine room-name]')
    else:
        hive = inp[0]
        remote_mine = inp[1]
        Memory.rooms[hive].remote_mines[remote_mine] = {}
