# defs is a package which claims to export all constants and some JavaScript objects, but in reality does
#  nothing. This is useful mainly when using an editor like PyCharm, so that it 'knows' that things like Object, Creep,
#  Game, etc. do exist.
from Misc.path_cacher import PathCache
from Misc.query_cacher import Cache
from controllers.hive_controller import HiveController
from defs import *

# These are currently required for Transcrypt in order to use the following names in JavaScript.
# Without the 'noalias' pragma, each of the following would be translated into something like 'py_Infinity' or
#  'py_keys' in the output file.
__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

if not Memory.creeps:
    Memory.creeps = {}
if not Memory.rooms:
    Memory.rooms = {}
if not Memory.flags:
    Memory.flags = {}


def main():
    """
    Main game logic loop.
    """
    cacher = Cache()
    for creep_name in Object.keys(Game.creeps):
        cacher.add_creep_to_cache(Game.creeps[creep_name])

    path_cache = PathCache()

    # remove dead creeps from memory (we dont care about the dead!)
    for creep_name in Object.keys(Memory.creeps):
        if not Object.keys(Game.creeps).includes(creep_name):
            del Memory.creeps[creep_name]


    # Run each hive.
    for room_name in Object.keys(Memory.rooms):
        if not Memory.rooms[room_name]:
            Memory.rooms[room_name] = {}
        hive_controller = HiveController(room_name, cacher, path_cache)
        hive_controller.run()

module.exports.loop = main
