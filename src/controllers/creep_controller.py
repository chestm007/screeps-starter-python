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


class CreepController(object):
    creep_type_map = {
        worker.Harvester.role: worker.Harvester,
        worker.Builder.role: worker.Builder,
        worker.Miner.role: worker.Miner,
        worker.Carrier.role: worker.Carrier,
        worker.Claimer.role: worker.Claimer,
        worker.RemoteMiner.role: worker.RemoteMiner,
        worker.RemoteCarrier.role: worker.RemoteCarrier,
        worker.RemoteBuilder.role: worker.RemoteBuilder,
        soldier.RemoteDefender.role: soldier.RemoteDefender
    }

    def __init__(self, cache):
        self.creeps = []  # type: list(Creep, )
        self.cache = cache
        self.initialize_creeps()

    def initialize_creeps(self):
        self.creeps = []
        for name in Object.keys(Game.creeps):
            creep = Game.creeps[name]
            if not creep.spawning:
                creep_class = self.get_creep_object_from_type(creep)
                if creep_class:
                    self.creeps.append(self.creep_type_map[creep.memory.role](self, creep))

    def run_creeps(self):
        for creep in self.creeps:
            creep.run_creep()

    def get_creep_object_from_type(self, creep):
        return self.creep_type_map[creep.memory.role]

    def say_roles(self):
        for c in self.creeps:
            c.creep.say(c.creep.memory.role)

