from components.cli.helpers import get_command
from components.cli.hive.add_remote_mine import add_remote_mine
from components.cli.hive.add import add
from components.cli.hive.remove import remove
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')


def hive(inp):
    command, args = get_command(inp)
    if command == 'add':
        add(args)
    elif command == 'remove':
        remove(args)
    elif command == 'add-remote-mine':
        add_remote_mine(args)
    elif command == 'remove-remote-mine':
        pass
    else:
        console.log('add                - add new hive to the register')
        console.log('remove             - remove an existing hive from the register')
        console.log('add-remote-mine    - add remote mine to hive')
        console.log('remove-remote-mine - remove remote mine from hive')
