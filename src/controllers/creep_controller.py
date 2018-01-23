from defs import *
import creep_factory

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
        'harvester': creep_factory.Harvester
    }

    creep_body_map = {
        '.'.join(creep_factory.SmallHarvester.body_composition): 'harvester',
        '.'.join(creep_factory.LargeHarvester.body_composition): 'harvester'
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
