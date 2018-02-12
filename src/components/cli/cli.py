from components.cli.helpers import get_command
from components.cli.hive.hive import hive
from components.cli.path_cache.path_cache import path_cache
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')


def cli_main(inp):
    if inp:
        command, args = get_command(inp.split(' '))
    else:
        command = None
        args = None
    if command == 'hive':
        hive(args)
    elif command == 'path-cache':
        path_cache(args)
    elif command == 'lowest-ttl':
        if len(args) != 1:
            console.log('[room-name]')
            return
        creeps = Game.rooms[args[0]].find(FIND_MY_CREEPS)
        lowest_ttl = _.min(creeps, lambda c: c.ticksToLive)
        console.log('lowest ttl: {} {}'.format(lowest_ttl.name, lowest_ttl.ticksToLive))
    else:
        console.log('hive       - Hive commands')
        console.log('path-cache - Path cache operations')
        console.log('lowest-ttl - find creep with lowest ttl in a room')