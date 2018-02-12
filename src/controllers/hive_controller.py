from controllers.creep_controller import CreepController
from controllers.remote_mine_controller import RemoteMineController
from controllers.tower_controller import TowerController
from creeps.hive_builder import HiveBuilder
from creeps.soldier.kiter import Kiter
from creeps.soldier.sumo import Sumo
from creeps.soldier.soldier import Soldier
from creeps.soldier.remote_defender import RemoteDefender
from creeps.worker.hive_claimer import HiveClaimer
from creeps.worker.worker import Worker, Builder, Harvester
from creeps.worker.carrier import Carrier
from creeps.worker.claimer import Claimer
from creeps.worker.miner import Miner
from creeps.worker.remote_builder import RemoteBuilder
from creeps.worker.remote_carrier import RemoteCarrier
from creeps.worker.remote_miner import RemoteMiner
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')
__pragma__('noalias', 'pop')

HARVESTER = Harvester.role
BUILDER = Builder.role
WORKER = Worker.role
MINER = Miner.role
CARRIER = Carrier.role
CLAIMER = Claimer.role
HIVE_CLAIMER = HiveClaimer.role
HIVE_BUILDER = HiveBuilder.role
REMOTE_MINER = RemoteMiner.role
REMOTE_CARRIER = RemoteCarrier.role
REMOTE_BUILDER = RemoteBuilder.role

SOLDIER = Soldier.role
REMOTE_DEFENDER = RemoteDefender.role
SUMO = Sumo.role
KITER = Kiter.role

CREEP_MAP = {
    HARVESTER: Harvester,
    BUILDER: Builder,
    WORKER: Worker,
    MINER: Miner,
    CARRIER: Carrier,
    CLAIMER: Claimer,
    HIVE_CLAIMER: HiveClaimer,
    HIVE_BUILDER: HiveBuilder,
    REMOTE_MINER: RemoteMiner,
    REMOTE_CARRIER: RemoteCarrier,
    REMOTE_BUILDER: RemoteBuilder,

    SOLDIER: Soldier,
    REMOTE_DEFENDER: RemoteDefender,
    SUMO: Sumo,
    KITER: Kiter
}


class HiveController:

    def __init__(self, room_name, cache, path_cache):
        self._name = room_name
        self.cache = cache
        self.path_cache = path_cache
        self.room = Game.rooms[self._name]

        spawns = [Game.spawns[spawn] for spawn in Object.keys(Game.spawns)]
        self.spawns = _.filter(spawns, lambda s: s.room.name == self._name)

        self.creeps = _.filter(Memory.creeps, lambda c: c.hive == self._name)
        self.creep_targets = [Memory.creeps[creep].target for creep in Memory.creeps if Memory.creeps[creep].hive == self._name]
        self.creep_controller = CreepController(self, cache)

        self.memory = self.room.memory
        self.min_workers = None
        self.max_carriers = None
        self.all_spawned = False
        self.max_workers = None

        # TOWERS ARE FUCKING IMPORTANT! THEY RUN FIRST!!
        self.tower_controller = TowerController(room_name)
        self.tower_controller.run_towers()

        if self.room.storage:
            self.storage = self.room.storage
        else:
            self.storage = None

        self.load_memory_settings()
        self.try_spawn_creeps()

        # Run all our mines in other rooms associated with this hive
        if not self.memory.remote_mines:
            self.memory.remote_mines = {}
        self.remote_mines = [
            RemoteMineController(self, mine_name) for mine_name in Object.keys(self.memory.remote_mines)
        ]

    def run(self):
        if self.storage:
            for remote_mine in self.remote_mines:
                remote_mine.run()
        self.creep_controller.run_creeps()
        # self.creep_controller.say_roles()

    def get_idle_spawn(self):
        for spawn in self.spawns:
            if not spawn.spawning:
                return spawn

    def try_spawn_creeps(self):
        for spawn in self.spawns:
            if not spawn.spawning:
                # Get the number of our creeps in the room.
                if spawn.room.energyAvailable >= 250:
                    hive_claimer_flags = _.filter(Game.flags, lambda f: f.name == self._name + '_hive_claim')
                    if len(Object.keys(hive_claimer_flags)) > 0:
                        hive_claimers = _.filter(self.creeps, lambda c: c.role == HIVE_CLAIMER)
                        if len(Object.keys(hive_claimers)) < len(Object.keys(hive_claimer_flags)):
                            self.create_creep(HIVE_CLAIMER, spawn, {'role': HiveClaimer.role,
                                                                    'flag': hive_claimer_flags[0],
                                                                    'hive': self._name})
                        else:
                            hive_builders = _.filter(self.creeps, lambda c: c.role == HIVE_BUILDER)
                            if len(Object.keys(hive_builders)) < 4:
                                self.create_creep(HIVE_BUILDER, spawn, {'role': HiveBuilder.role,
                                                                        'flag': hive_claimer_flags[0],
                                                                        'hive': self._name})

                    num_workers = _.sum(self.creeps, lambda c: c.room == spawn.pos.roomName and
                                                               (c.role == HARVESTER or c.role == BUILDER))
                    if (num_workers < self.min_workers
                            or (num_workers < self.max_workers
                                and spawn.room.energyAvailable >= spawn.room.energyCapacityAvailable)):
                        self.create_creep(WORKER, spawn, {'role': Harvester.role,
                                                          'room': self._name,
                                                          'hive': self._name})
                    else:

                        if num_workers >= self.min_workers:
                            # Ensure number of miners = number of resource points
                            num_miners = _.sum(self.creeps, lambda c: c.room == spawn.pos.roomName and
                                                                      (c.role == MINER))
                            if num_miners < len(spawn.room.find(FIND_SOURCES)):
                                self.create_creep(MINER, spawn, {'role': Miner.role,
                                                                 'room': self._name,
                                                                 'hive': self._name})

                            else:
                                # ensure number of carriers is max_carriers if set, or = number of miners
                                num_carriers = _.sum(self.creeps, lambda c: c.room == spawn.pos.roomName and
                                                                            (c.role == CARRIER))
                                if spawn.room.energyAvailable < spawn.room.controller.level * 300 and num_carriers > 1:
                                    return
                                if num_carriers < self.max_carriers:
                                    self.create_creep(CARRIER, spawn, {'role': Carrier.role,
                                                                       'room': self._name,
                                                                       'hive': self._name})
                                else:
                                    self.all_spawned = True
                                    hive_attack_flags = _.filter(Game.flags, lambda f: f.name.startswith(self._name + '_attack')
                                                                                       or f.name.startswith('all_attack')
                                                                 )
                                    if len(Object.keys(hive_attack_flags)) > 0:
                                        for flag in hive_attack_flags:
                                            c_type = flag.name.split('_attack_')[1]
                                            if c_type:
                                                self.create_creep(c_type, spawn, {'role': c_type,
                                                                                  'flag': flag.name,
                                                                                  'hive': self._name})
                                    kite_attack_flags = _.filter(Game.flags, lambda f: f.name.startswith(self._name + '_kite')
                                                                                       or f.name.startswith('all_attack'))
                                    num_kiters = _.sum(self.creeps, lambda c: c.hive == spawn.pos.roomName and
                                                                              (c.role == KITER))
                                    if len(Object.keys(kite_attack_flags)) > 0:
                                        if num_kiters < 6:
                                            for flag in kite_attack_flags:
                                                self.create_creep(KITER, spawn, {'role': Kiter.role,
                                                                                 'flag': flag.name,
                                                                                 'hive': self._name})

    def create_creep(self, creep_type, spawn, memory):
        if memory == undefined:
            console.log('attempted to create a creep with no memory!: type: {}, spawn:{}, hive:{}'.format(
                creep_type, spawn.name, self._name))
            return

        return CREEP_MAP[creep_type].factory(spawn, memory)

    def create_creep_with_body(self, creep_type, spawn, memory, body):
        if memory == undefined:
            console.log('attempted to create a creep with no memory!: type: {}, spawn:{}, hive:{}'.format(
                creep_type, spawn.name, self._name))
            return

        return CREEP_MAP[creep_type].factory_with_body(spawn, memory, body)

    def load_memory_settings(self):
        # ensure Memory.rooms[this_room].settings exists and is a dict
        if not self.memory.settings:
            self.memory.settings = {}

        # load settings if set, or use defaults
        # minimum workers for this room
        self.min_workers = self.memory.settings.min_workers
        if not self.min_workers:
            self.memory.settings.min_workers = 3
            self.min_workers = self.memory.settings.min_workers

        # maximum workers for this room
        self.max_workers = self.memory.settings.max_workers
        if not self.max_workers:
            self.memory.settings.max_workers = 6
            self.max_workers = self.memory.settings.max_workers

        # maximum resource carriers for this room
        self.max_carriers = self.memory.settings.max_carriers
        if not self.max_carriers:
            self.memory.settings.max_carriers = 2
            self.max_carriers = self.memory.settings.max_carriers
