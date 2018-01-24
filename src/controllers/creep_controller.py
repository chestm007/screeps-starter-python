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
        'harvester': worker.Harvester,
        'builder': worker.Builder
    }

    creep_body_map = {
        '.'.join(worker.Worker.body_composition['small']): 'harvester',
        '.'.join(worker.Worker.body_composition['medium']): 'harvester',
        '.'.join(worker.Worker.body_composition['large']): 'harvester'
    }

    @staticmethod
    def run_creep(creep):
        creep_class = CreepController.get_creep_object_from_type(creep)
        # if this creep is currently unclassified
        if not creep_class:
            creep_type = CreepController.creep_body_map['.'.join([i.type for i in creep.body])]
            if not creep_type:
                console.log('uncategorizable creep detected: {}'.format(creep.name))
                return
            creep.memory.role = creep_type
            creep_class = CreepController.creep_type_map[creep.memory.role]
        creep_class.run_creep(creep)

    @staticmethod
    def get_creep_object_from_type(creep):
        return CreepController.creep_type_map[creep.memory.role]

    @staticmethod
    def say_role(creep):
        creep.say(creep.memory.role)

