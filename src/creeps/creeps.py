from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')


class Creeps:
    role = None
    body_composition = None

    def __init__(self, controller, creep, hive):
        self.creep = creep
        self.controller = controller
        self.hive = hive
        self.room_cache = self.controller.cache.get_room_cache(creep.room)
        self.structures_in_room = self.room_cache.get_structures()
        self.construction_sites_in_room = self.room_cache.get_construction_sites()
        self.resources_in_room = self.room_cache.get_resources()
        self.dropped_resources_in_room = self.room_cache.get_dropped_resources()

    @staticmethod
    def _calculate_creation_cost(body_composition):
        if body_composition:
            return sum([BODYPART_COST[part] for part in body_composition])

    @classmethod
    def factory(cls, spawn, memory):
        i = len(cls.body_composition)
        while True:
            i -= 1
            if i < 0:
                break
            if spawn.room.energyAvailable >= cls._calculate_creation_cost(cls.body_composition[i]):
                body = cls.body_composition[i]

                console.log('spawning new {} {} creep'.format(i, cls.__name__))
                memory['role'] = cls.role
                return Creeps.create(body, spawn, memory)

    @classmethod
    def factory_with_body(cls, spawn, memory, body):
        i = cls.body_composition
        if spawn.room.energyAvailable >= cls._calculate_creation_cost(body):
            console.log('spawning new {} {} creep'.format(i, cls.__name__))
            memory['role'] = cls.role
            return Creeps.create(body, spawn, memory)

    @classmethod
    def create(cls, body, spawn, memory):
        if body is None:
            console.log('Error creating {}: no defined body composition'.format(cls.__name__))
        else:
            name = spawn.name + Game.time
            spawn.spawnCreep(body, name, {'memory': memory})

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

    def move_by_cached_path(self, target: RoomObject):
        pos = self.pos_to_string(self.creep.pos)
        if self.creep.memory.last_pos != pos:
            self.creep.memory.last_pos = pos
            if target:
                if target.pos:
                    t = target.pos
                else:
                    t = target
                path = self.hive.path_cache.get_path(self.creep.pos, t)
                res = self.creep.moveByPath(path)
                if res != OK and res != ERR_TIRED:
                    console.log(self.creep.name, res)
                self.creep.memory.stuck_counter = 0
                return True
        else:
            if not self.creep.memory.stuck_counter:
                self.creep.memory.stuck_counter = 1
            else:
                self.creep.memory.stuck_counter += 1
            if self.creep.memory.stuck_counter > 3:
                self.creep.moveTo(target)
                return False

    @staticmethod
    def pos_to_string(pos):
        return pos.x + 'x' + pos.y
