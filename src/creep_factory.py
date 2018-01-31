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
CARRIER = worker.Carrier.role
CLAIMER = worker.Claimer.role


def create_creep(creep_type, spawn, num_workers):
    if creep_type == WORKER:
        worker.Worker.factory(spawn, 9)
    if creep_type == SOLDIER:
        soldier.Soldier.factory(spawn, 9)
    if creep_type == MINER:
        worker.Miner.factory(spawn, 9)
    if creep_type == CARRIER:
        worker.Carrier.factory(spawn, 9)
    if creep_type == CLAIMER:
        worker.Claimer.factory(spawn, 9)


def try_create_creep(spawn):
    if not spawn.spawning:
        # Get the number of our creeps in the room.
        if spawn.room.energyAvailable >= 250:
            if not Object.keys(Memory.rooms).includes(spawn.room.name):
                Memory.rooms[spawn.room.name] = {}
            if not Memory.rooms[spawn.room.name].settings:
                Memory.rooms[spawn.room.name].settings = {}
            min_workers = Memory.rooms[spawn.room.name].settings.min_workers
            if not min_workers:
                Memory.rooms[spawn.room.name].settings.min_workers = 3
                min_workers = 3

            max_workers = Memory.rooms[spawn.room.name].settings.max_workers
            if not max_workers:
                Memory.rooms[spawn.room.name].settings.max_workers = 6
                max_workers = 6

            max_carriers = Memory.rooms[spawn.room.name].settings.max_carriers
            num_workers = _.sum(Game.creeps, lambda c: c.pos.roomName == spawn.pos.roomName and
                                                       (c.memory.role == HARVESTER or c.memory.role == BUILDER))
            # If there are less than 3 creeps, spawn a creep once energy is at 250 or more
            # If there are less than 10 creeps but at least one, wait until all spawns and extensions are full before
            # spawning.
            if (
                                num_workers < min_workers
                    or num_workers < max_workers and spawn.room.energyAvailable >= spawn.room.energyCapacityAvailable):
                create_creep(WORKER, spawn, num_workers)

            num_miners = _.sum(Game.creeps, lambda c: c.pos.roomName == spawn.pos.roomName and
                                                       (c.memory.role == MINER))
            if num_miners < len(spawn.room.find(FIND_SOURCES)):
                create_creep(MINER, spawn, num_miners)

            num_carriers = _.sum(Game.creeps, lambda c: c.pos.roomName == spawn.pos.roomName and
                                                      (c.memory.role == CARRIER))

            if not max_carriers:
                max_carriers = num_miners
            if num_carriers < max_carriers:
                create_creep(CARRIER, spawn, num_carriers)

            num_claimers = _.sum(Game.creeps, lambda c: c.memory.role == CLAIMER)
            if num_claimers < len(Object.keys(Game.flags)):
                create_creep(CLAIMER, spawn, None)

