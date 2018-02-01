from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class Creeps(object):
    body_composition = None
    body_part_cost = {
        MOVE: 50,
        WORK: 100,
        CARRY: 50,
        ATTACK: 80,
        RANGED_ATTACK: 150,
        HEAL: 250,
        TOUGH: 10,
        CLAIM: 600
    }

    def __init__(self, controller, creep):
        self.creep = creep
        self.controller = controller
        self.structures_in_room = self.controller.cache.get_room_cache(creep.room).get_structures()
        self.construction_sites_in_room = self.controller.cache.get_room_cache(creep.room).get_construction_sites()
        self.resources_in_room = self.controller.cache.get_room_cache(creep.room).get_resources()
        self.dropped_resources_in_room = self.controller.cache.get_room_cache(creep.room).get_dropped_resources()

    num_creep_to_size = ['small', 'small', 'medium', 'medium', 'large', 'xlarge']

    @staticmethod
    def _calculate_creation_cost(body_composition):
        return sum([Creeps.body_part_cost[part] for part in body_composition])

    @staticmethod
    def factory(spawn, num_workers):
        pass

    @staticmethod
    def create(body, spawn, role):
        if body is None:
            console.log('Error creating {}: no defined body composition'.format(role))
        else:
            spawn.createCreep(body, None, {'role': role})

    def run_creep(self):
        console.log('cannot run undefined creep {}'.format(self.creep.name))
