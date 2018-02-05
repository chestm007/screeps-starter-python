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

    #'.'.join(worker..body_composition['small'] ): worker..role,
    #'.'.join(worker..body_composition['medium']): worker..role,
    #'.'.join(worker..body_composition['large'] ): worker..role,
    #'.'.join(worker..body_composition['xlarge']): worker..role,
    creep_body_map = {
        '.'.join(worker.Worker.body_composition['small']): worker.Harvester.role,
        '.'.join(worker.Worker.body_composition['medium']): worker.Harvester.role,
        '.'.join(worker.Worker.body_composition['large']): worker.Harvester.role,
        '.'.join(worker.Worker.body_composition['xlarge']): worker.Harvester.role,
        '.'.join(worker.Miner.body_composition['small']): worker.Miner.role,
        '.'.join(worker.Miner.body_composition['medium']): worker.Miner.role,
        '.'.join(worker.Miner.body_composition['large']): worker.Miner.role,
        '.'.join(worker.Miner.body_composition['xlarge']): worker.Miner.role,
        '.'.join(worker.Carrier.body_composition['small']): worker.Carrier.role,
        '.'.join(worker.Carrier.body_composition['medium']): worker.Carrier.role,
        '.'.join(worker.Carrier.body_composition['large']): worker.Carrier.role,
        '.'.join(worker.Carrier.body_composition['xlarge']): worker.Carrier.role,
        '.'.join(worker.RemoteMiner.body_composition['small']): worker.RemoteMiner.role,
        '.'.join(worker.RemoteMiner.body_composition['medium']): worker.RemoteMiner.role,
        '.'.join(worker.RemoteMiner.body_composition['large']): worker.RemoteMiner.role,
        '.'.join(worker.RemoteMiner.body_composition['xlarge']): worker.RemoteMiner.role,
        '.'.join(worker.RemoteCarrier.body_composition['large']): worker.RemoteCarrier.role,
        '.'.join(worker.RemoteBuilder.body_composition['large']): worker.RemoteBuilder.role,
        '.'.join(soldier.RemoteDefender.body_composition['large']): soldier.RemoteDefender.role,
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
                if not creep_class:
                    creep_type = self.creep_body_map['.'.join([i.type for i in creep.body])]
                    if not creep_type:
                        console.log('uncategorizable creep detected: {}'.format(creep.name))
                        return
                    #creep.memory.role = creep_type
                self.creeps.append(self.creep_type_map[creep.memory.role](self, creep))

    def run_creeps(self):
        for creep in self.creeps:
            creep.run_creep()

    def get_creep_object_from_type(self, creep):
        return self.creep_type_map[creep.memory.role]

    def say_roles(self):
        for c in self.creeps:
            c.creep.say(c.creep.memory.role)

