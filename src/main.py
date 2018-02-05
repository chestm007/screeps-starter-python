import creep_factory
# defs is a package which claims to export all constants and some JavaScript objects, but in reality does
#  nothing. This is useful mainly when using an editor like PyCharm, so that it 'knows' that things like Object, Creep,
#  Game, etc. do exist.
from Misc.query_cacher import Cache
from controllers.creep_controller import CreepController
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
    # console.log('missing remote creeps')
    # console.log('builders: ', cacher.miss_builders)
    # console.log('claimers: ', cacher.miss_claimers)
    # console.log('carriers: ', cacher.miss_carriers)
    # console.log('miners: ', cacher.miss_miners)
    # console.log('defenders: ', cacher.miss_defenders)

    if not Memory.rooms:
        Memory.rooms = {}

    # remove dead creeps from memory (we dont care about the dead!)
    for creep_name in Object.keys(Memory.creeps):
        if not Object.keys(Game.creeps).includes(creep_name):
            del Memory.creeps[creep_name]


    # Run each tower (shoot things and heal stuff)
    for room_name in Object.keys(Memory.rooms):
        hive_controller = HiveController(room_name)
        #hive_controller.run()
    # Run each spawn (replace dead creeps with moar minions)
    # TODO: move to HiveController()
    for name in Object.keys(Game.spawns):
        creep_factory.try_create_creep(Game.spawns[name], cacher)

    # Run each creep
    # TODO: move to HiveController()
    creep_controller = CreepController(cacher)
    creep_controller.run_creeps()
    creep_controller.say_roles()

module.exports.loop = main
