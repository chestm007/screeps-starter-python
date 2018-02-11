from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')


def remove(inp):
    if len(inp) != 1:
        console.log('[room-name]')
    else:
        hive_name = inp[0]
        del Memory.rooms[hive_name]
