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
MINER = worker.Miner.role
CARRIER = worker.Carrier.role
CLAIMER = worker.Claimer.role
REMOTE_MINER = worker.RemoteMiner.role
REMOTE_CARRIER = worker.RemoteCarrier.role
REMOTE_BUILDER = worker.RemoteBuilder.role

SOLDIER = soldier.Soldier.role
REMOTE_DEFENDER = soldier.RemoteDefender.role
SUMO = soldier.Sumo.role


def create_creep(creep_type, spawn, num_creeps, extra_memory_args):
    if creep_type == WORKER:
        return worker.Worker.factory(spawn, 9, None)
    elif creep_type == MINER:
        return worker.Miner.factory(spawn, 9, None)
    elif creep_type == CARRIER:
        return worker.Carrier.factory(spawn, num_creeps, None)
    elif creep_type == CLAIMER:
        return worker.Claimer.factory(spawn, 9, extra_memory_args)
    elif creep_type == REMOTE_MINER:
        return worker.RemoteMiner.factory(spawn, 9, extra_memory_args)
    elif creep_type == REMOTE_CARRIER:
        return worker.RemoteCarrier.factory(spawn, 9, extra_memory_args)
    elif creep_type == REMOTE_BUILDER:
        return worker.RemoteBuilder.factory(spawn, 9, extra_memory_args)
    elif creep_type == SOLDIER:
        return soldier.Soldier.factory(spawn, 9, None)
    elif creep_type == REMOTE_DEFENDER:
        return soldier.RemoteDefender.factory(spawn, 9, None)
    elif creep_type == SUMO:
        return soldier.Sumo.factory(spawn, 9, None)
    else:
        console.log('unrecognised creep type detected {}'.format(creep_type))


def try_create_creep(spawn, cache):
    if not spawn.spawning:
        if not Memory.rooms[spawn.room.name]:
            Memory.rooms[spawn.room.name] = {}
        if not Memory.rooms[spawn.room.name].spawn:
            Memory.rooms[spawn.room.name].spawn = spawn.name
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
            if (num_workers < min_workers
                or
                    (
                                    num_workers < max_workers
                            and spawn.room.energyAvailable >= spawn.room.energyCapacityAvailable)):
                create_creep(WORKER, spawn)
            if num_workers >= min_workers:
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
                    create_creep(CARRIER, spawn, num_carriers)

                # if spawn.room.storage:
                #     if spawn.room.storage.store[RESOURCE_ENERGY] > 20000:
                #         i = 0
                #         while True:
                #             remote_prefix, creep_type = None, None
                #             if len(cache.miss_defenders) > i:
                #                 remote_prefix = cache.miss_defenders[i]
                #                 creep_type = REMOTE_DEFENDER
                #                 flag = remote_prefix
                #                 if _check_and_spawn(spawn, remote_prefix + 'Spawn',  flag, cache, creep_type):
                #                     break
                #             if len(cache.miss_claimers) > i:
                #                 remote_prefix = cache.miss_claimers[i]
                #                 creep_type = CLAIMER
                #                 flag = remote_prefix
                #                 if _check_and_spawn(spawn, remote_prefix + 'Spawn',  flag, cache, creep_type):
                #                     break
                #             # if len(cache.miss_builders) > i:
                #             #     remote_prefix = cache.miss_builders[i]
                #             #     flag = remote_prefix
                #             #     creep_type = REMOTE_BUILDER
                #             #     if _check_and_spawn(spawn, remote_prefix + 'Spawn', flag, cache, creep_type):
                #             #         break
                #             if len(cache.miss_miners) > i:
                #                 remote_prefix = cache.miss_miners[i]
                #                 creep_type = REMOTE_MINER
                #                 flag = remote_prefix
                #                 if _check_and_spawn(spawn, remote_prefix + 'Spawn',  flag, cache, creep_type):
                #                     break
                #             if len(cache.miss_carriers) > i:
                #                 remote_prefix = cache.miss_carriers[i]
                #                 if not cache.miss_miners.includes(remote_prefix):
                #                     creep_type = REMOTE_CARRIER
                #                     flag = remote_prefix + 'Storage'
                #                     if _check_and_spawn(spawn, remote_prefix + 'Spawn',  flag, cache, creep_type):
                #                         break
                #             if not remote_prefix:
                #                 break
                #             i += 1


def _check_and_spawn(cur_spawn, spawn_flag, flag, cache, creep_type):
    for room in Object.keys(Memory.rooms):
        if cache.rooms[room]:
            if cache.rooms[room].associated_remote_mines:
                if cache.rooms[room].associated_remote_mines.includes(spawn_flag):
                    if cur_spawn.room.name == room:
                        if create_creep(creep_type, cur_spawn, extra_memory_args={'flag': flag}) == OK:
                            console.log('remote_spawn_creep:', creep_type, cur_spawn, flag)
                            return True
