from creeps.worker import Worker
from creeps.soldier import Soldier
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

HARVESTER = 'harvester'
SOLDIER = 'soldier'


def create_creep(creep_type, spawn):
    if creep_type == HARVESTER:
        Worker.factory(spawn)
    if creep_type == SOLDIER:
        Soldier.factory(spawn)


def _should_create_creep(spawn):
    if not spawn.spawning:
        # Get the number of our creeps in the room.
        num_creeps = _.sum(Game.creeps, lambda c: c.pos.roomName == spawn.pos.roomName)
        # If there are less than 3 creeps, spawn a creep once energy is at 250 or more
        # If there are less than 10 creeps but at least one, wait until all spawns and extensions are full before
        # spawning.
        if num_creeps < 3 and spawn.room.energyAvailable >= 250:
            return HARVESTER

        elif num_creeps < 6 and spawn.room.energyAvailable >= spawn.room.energyCapacityAvailable:
            return HARVESTER


def try_create_creep(spawn):
    creep_type = _should_create_creep(spawn)
    if creep_type:
        create_creep(creep_type, spawn)
