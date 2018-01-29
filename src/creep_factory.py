from creeps import worker
from creeps import soldier
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

HARVESTER = worker.Harvester.role
BUILDER = worker.Builder.role
WORKER = worker.Worker.role
SOLDIER = soldier.Soldier.role
MINER = worker.Miner.role


def create_creep(creep_type, spawn, num_workers):
    if creep_type == WORKER:
        worker.Worker.factory(spawn, num_workers)
    if creep_type == SOLDIER:
        soldier.Soldier.factory(spawn, num_workers)
    if creep_type == MINER:
        worker.Miner.factory(spawn, num_workers)


def try_create_creep(spawn):
    if not spawn.spawning:
        # Get the number of our creeps in the room.
        num_workers = _.sum(Game.creeps, lambda c: c.pos.roomName == spawn.pos.roomName and
                                                   (c.memory.role == HARVESTER or c.memory.role == BUILDER))
        # If there are less than 3 creeps, spawn a creep once energy is at 250 or more
        # If there are less than 10 creeps but at least one, wait until all spawns and extensions are full before
        # spawning.
        if (
                            num_workers < 3 and spawn.room.energyAvailable >= 250
                or num_workers < 6 and spawn.room.energyAvailable >= spawn.room.energyCapacityAvailable):
            create_creep(WORKER, spawn, num_workers)
            return

        if len(spawn.room.find(FIND_STRUCTURES).filter(
            lambda s: s.structureType == STRUCTURE_CONTAINER
        )) > 0:
            num_miners = _.sum(Game.creeps, lambda c: c.pos.roomName == spawn.pos.roomName and
                                                       (c.memory.role == MINER))
            if num_miners < len(spawn.room.find(FIND_SOURCES)):
                create_creep(MINER, spawn, num_miners)

