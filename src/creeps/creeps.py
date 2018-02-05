from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')


class Creeps(object):
    role = None
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
        self.room_cache = self.controller.cache.get_room_cache(creep.room)
        self.structures_in_room = self.room_cache.get_structures()
        self.construction_sites_in_room = self.room_cache.get_construction_sites()
        self.resources_in_room = self.room_cache.get_resources()
        self.dropped_resources_in_room = self.room_cache.get_dropped_resources()

    num_creep_to_size = ['small', 'small', 'medium', 'medium', 'large', 'xlarge']

    @staticmethod
    def _calculate_creation_cost(body_composition):
        return sum([Creeps.body_part_cost[part] for part in body_composition])

    @classmethod
    def factory(cls, spawn, memory):
        i = len(cls.body_composition)
        while True:
            i -= 1
            if spawn.room.energyAvailable >= cls._calculate_creation_cost(cls.body_composition[i]):
                body = cls.body_composition[i]

                console.log('spawning new {} {} creep'.format(i, cls.__name__))
                memory['role'] = cls.role
                return Creeps.create(body, spawn, memory)

    @staticmethod
    def create(body, spawn, role, extra_memory_args):
        if body is None:
            console.log('Error creating {}: no defined body composition'.format(role))
        else:
            spawn.createCreep(body, None, {'role': role})

    def run_creep(self):
        console.log('cannot run undefined creep {}'.format(self.creep.name))

    def get_closest_to_creep(self, obj_list):
        closest = None
        least_distance = 1000
        for r in obj_list:
            distance_to_creep = r.pos.getRangeTo(self.creep.pos)
            if distance_to_creep < least_distance:
                least_distance = distance_to_creep
                closest = r
        return closest
