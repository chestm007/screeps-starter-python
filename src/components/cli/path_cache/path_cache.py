from Misc.path_cacher import PathCache
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')


def path_cache(inp):
    if len(inp) != 1:
        pass
    elif inp[0] == 'clear':
        Memory.path_cache = {}
        return
    elif inp[0] == 'clean':
        path_cacher = PathCache()
        path_cacher.clean_cache()
        return
    elif inp[0] == 'size':
        console.log('pathcache size: {} entries'.format(len(Object.keys(Memory.path_cache))))

    console.log('clear - clear the path cache ENTIRELY')
    console.log('clean - clean the path cache to a predefined number of entries based on usage')