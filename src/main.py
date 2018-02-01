import creep_factory
# defs is a package which claims to export all constants and some JavaScript objects, but in reality does
#  nothing. This is useful mainly when using an editor like PyCharm, so that it 'knows' that things like Object, Creep,
#  Game, etc. do exist.
from Misc.query_cacher import Cache
from controllers.creep_controller import CreepController
from controllers.planner_controller import PlannerController
from controllers.tower_controller import TowerController
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


def main():
    """
    Main game logic loop.
    """
    cacher = Cache()
    for creep_name in Object.keys(Game.creeps):
        cacher.add_room_to_cache(Game.creeps[creep_name].room)
    if not Memory.rooms:
        Memory.rooms = {}
    # Perform Scheduled planning tasks
    #PlannerController.run()

    # remove dead creeps from memory (we dont care about the dead!)
    for creep_name in Object.keys(Memory.creeps):
        if not Object.keys(Game.creeps).includes(creep_name):
            del Memory.creeps[creep_name]

    # Run each spawn (replace dead creeps with moar minions)
    for name in Object.keys(Game.spawns):
        creep_factory.try_create_creep(Game.spawns[name])

    # Run each tower (shoot things and heal stuff)
    for room in Object.keys(Memory.rooms):
        tower_controller = TowerController(room)
        tower_controller.run_towers()

    # Run each creep
    creep_controller = CreepController(cacher)
    creep_controller.run_creeps()
    creep_controller.say_roles()

module.exports.loop = main
