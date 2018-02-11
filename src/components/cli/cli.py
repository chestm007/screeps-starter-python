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
    command, args = get_command(inp.split(' '))
    if command == 'hive':
        hive(args)
    if command == 'path-cache':
        path_cache(args)
    else:
        console.log('hive       - Hive commands')
        console.log('path-cache - Path cache operations')
