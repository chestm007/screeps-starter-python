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
REMOTE_MINER = worker.RemoteMiner.role
REMOTE_CARRIER = worker.RemoteCarrier.role


def create_creep(creep_type, spawn):
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
    if creep_type == REMOTE_MINER:
        worker.RemoteMiner.factory(spawn, 9)
    if creep_type == REMOTE_CARRIER:
        worker.RemoteCarrier.factory(spawn, 9)


def try_create_creep(spawn):
    if not spawn.spawning:
        # Get the number of our creeps in the room.
        if spawn.room.energyAvailable >= 250:

            # ensure this spawns room_name is in Memory.rooms
            if not Object.keys(Memory.rooms).includes(spawn.room.name):
                Memory.rooms[spawn.room.name] = {}

            # ensure Memory.rooms[this_room].settings exists and is a dict
            if not Memory.rooms[spawn.room.name].settings:
                Memory.rooms[spawn.room.name].settings = {}

            # load settings if set, or use defaults
            # minimum workers for this room
            min_workers = Memory.rooms[spawn.room.name].settings.min_workers
            if not min_workers:
                Memory.rooms[spawn.room.name].settings.min_workers = 3
                min_workers = 3

            # maximum workers for this room
            max_workers = Memory.rooms[spawn.room.name].settings.max_workers
            if not max_workers:
                Memory.rooms[spawn.room.name].settings.max_workers = 6
                max_workers = 6

            # maximum resource carriers for this room
            max_carriers = Memory.rooms[spawn.room.name].settings.max_carriers
            num_workers = _.sum(Game.creeps, lambda c: c.pos.roomName == spawn.pos.roomName and
                                                       (c.memory.role == HARVESTER or c.memory.role == BUILDER))
            if (
                                num_workers < min_workers
                    or num_workers < max_workers and spawn.room.energyAvailable >= spawn.room.energyCapacityAvailable):
                create_creep(WORKER, spawn)

            # Ensure number of miners = number of resource points
            num_miners = _.sum(Game.creeps, lambda c: c.pos.roomName == spawn.pos.roomName and
                                                       (c.memory.role == MINER))
            if num_miners < len(spawn.room.find(FIND_SOURCES)):
                create_creep(MINER, spawn)

            # ensure number of carriers is max_carriers if set, or = number of miners
            num_carriers = _.sum(Game.creeps, lambda c: c.pos.roomName == spawn.pos.roomName and
                                                      (c.memory.role == CARRIER))
            if not max_carriers:
                max_carriers = num_miners
            if num_carriers < max_carriers:
                create_creep(CARRIER, spawn)

            # create a claimer for every claim# flag placed
            # TODO: work out a naming scheme for desired spawns to be constructed, using flag as marker
            num_claimers = _.sum(Game.creeps, lambda c: c.memory.role == CLAIMER)
            if num_claimers < len([key for key in Object.keys(Game.flags) if str(key).startswith('claim')]):
                create_creep(CLAIMER, spawn)

            if spawn.room.storage.store[RESOURCE_ENERGY] > 20000:
                # create a remote miner for every RemoteMine# flag created
                num_remote_miners = _.sum(Game.creeps, lambda c: c.memory.role == REMOTE_MINER)
                if num_remote_miners < len([key for key in Object.keys(Game.flags)
                                            if str(key).startswith('RemoteMine')
                                            and not str(key).endswith('Storage')
                                            and not str(key).endswith('Spawn')]):
                    pass
                    create_creep(REMOTE_MINER, spawn)

                # create a remote carrier for every remote miner
                num_remote_carriers = _.sum(Game.creeps, lambda c: c.memory.role == REMOTE_CARRIER)
                if num_remote_carriers < num_remote_miners:
                    create_creep(REMOTE_CARRIER, spawn)

