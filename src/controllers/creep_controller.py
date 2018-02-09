from creeps.hive_builder import HiveBuilder
from creeps.soldier.kiter import Kiter
from creeps.soldier.remote_defender import RemoteDefender
from creeps.soldier.sumo import Sumo
from creeps.worker.hive_claimer import HiveClaimer
from creeps.worker.worker import Builder, Harvester
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


class CreepController(object):
    creep_type_map = {
        Harvester.role: Harvester,
        Builder.role: Builder,
        Miner.role: Miner,
        Carrier.role: Carrier,
        Claimer.role: Claimer,
        HiveClaimer.role: HiveClaimer,
        HiveBuilder.role: HiveBuilder,
        RemoteMiner.role: RemoteMiner,
        RemoteCarrier.role: RemoteCarrier,
        RemoteBuilder.role: RemoteBuilder,
        RemoteDefender.role: RemoteDefender,
        Sumo.role: Sumo,
        Kiter.role: Kiter,
    }

    def __init__(self, hive, cache):
        self.cache = cache
        self.hive = hive
        self.creeps = self.initialize_creeps()  # type: list(Creep(), )

    def initialize_creeps(self):
        out_creeps = []
        for creep in Object.keys(Game.creeps):
            creep = Game.creeps[creep]
            if creep:
                if creep.memory.hive == self.hive._name:
                    if not creep.spawning:
                        creep_class = self.get_creep_object_from_type(creep)
                        if creep_class:
                            out_creeps.append(self.creep_type_map[creep.memory.role](self, creep, self.hive))
        return out_creeps

    def run_creeps(self):
        for creep in self.creeps:
            creep.run_creep()

    def get_creep_object_from_type(self, creep):
        return self.creep_type_map[creep.memory.role]

    def say_roles(self):
        for c in self.creeps:
            c.creep.say(c.creep.memory.role)

