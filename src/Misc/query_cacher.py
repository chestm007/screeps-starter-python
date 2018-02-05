from creeps import soldier
from creeps import worker
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

CLAIMER = worker.Claimer.role
REMOTE_MINER = worker.RemoteMiner.role
REMOTE_CARRIER = worker.RemoteCarrier.role
REMOTE_BUILDER = worker.RemoteBuilder.role
REMOTE_DEFENDER = soldier.RemoteDefender.role


class Cache:
    def __init__(self):
        self.rooms = {}
        self.creeps = []

        self.has_remote_carriers = []
        self.has_remote_miners = []
        self.has_claimers = []
        self.has_remote_builders = []
        self.has_remote_defenders = []

        self.miss_carriers = []
        self.miss_miners = []
        self.miss_claimers = []
        self.miss_builders = []
        self.miss_defenders = []

    def add_creep_to_cache(self, creep):
        self.creeps.append(creep)

        if creep.memory.flag:
            flag = creep.memory.flag
            if flag.startswith('RemoteMine') or flag.startswith('reserve') or flag.startswith('claim'):
                if creep.memory.role == CLAIMER:
                    self.has_claimers.append(creep.memory.flag.replace('Spawn', ''))
                elif creep.memory.role == REMOTE_MINER:
                    self.has_remote_miners.append(creep.memory.flag)
                elif creep.memory.role == REMOTE_CARRIER:
                    self.has_remote_carriers.append(creep.memory.flag)
                elif creep.memory.role == REMOTE_BUILDER:
                    self.has_remote_builders.append(creep.memory.flag.replace('Spawn', ''))
                elif creep.memory.role == REMOTE_DEFENDER:
                    self.has_remote_defenders.append(creep.memory.flag.replace('Spawn', ''))

        if not self.rooms[creep.room.name]:
            self.rooms[creep.room.name] = RoomCache(creep.room)

    def get_room_cache(self, room):
        return self.rooms[room.name]

    def build_missing_creeps(self):
        for flag in Object.keys(Game.flags):
            if not flag.endswith('Spawn'):
                if flag.startswith('reserve'):
                    if not self.has_claimers.includes(flag):
                        self.miss_claimers.append(flag.replace('Spawn', ''))
                    if not self.has_remote_defenders.includes(flag):
                        self.miss_defenders.append(flag.replace('Spawn', ''))
                    if not self.has_remote_builders.includes(flag.replace('Spawn', '')):
                        self.miss_builders.append(flag.replace('spawn', ''))
                elif flag.startswith('RemoteMine'):
                    if flag.endswith('Storage'):
                        if not self.has_remote_carriers.includes(flag):
                            self.miss_carriers.append(flag.replace('Storage', ''))
                    else:
                        if not self.has_remote_miners.includes(flag):
                            self.miss_miners.append(flag)


class RoomCache:
    def __init__(self, room: Room):
        self.room = room
        self.spawn = None
        self.associated_remote_mines = None
        if Object.keys(Memory.rooms).includes(self.room.name):
            if Memory.rooms[self.room.name].spawn:
                self.spawn = Game.spawns[Memory.rooms[self.room.name].spawn]
                if self.spawn:
                    self.associated_remote_mines = [flag.name for flag in self.spawn.pos.lookFor(LOOK_FLAGS)]
        self.structures = None
        self.construction_sites = None
        self.resources = None
        self.dropped_resources = None
        self.remote_hostile_creeps = []

    def get_structures(self):
        if self.structures is None:
            self.structures = self.room.find(FIND_STRUCTURES)
        return self.structures

    def get_construction_sites(self):
        if self.construction_sites is None:
            self.construction_sites = self.room.find(FIND_CONSTRUCTION_SITES)
        return self.construction_sites

    def get_resources(self):
        if self.resources is None:
            self.resources = self.room.find(FIND_SOURCES)
        return self.resources

    def get_dropped_resources(self):
        if self.dropped_resources is None:
            self.dropped_resources = self.room.find(FIND_DROPPED_RESOURCES)
        return self.dropped_resources

    def put_remote_hostile_creep(self, creep):
        self.remote_hostile_creeps.append(creep)
