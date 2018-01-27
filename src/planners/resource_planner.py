from creep_factory import HARVESTER, MINER
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


class ResourcePlanner(object):
    @staticmethod
    def main():
        for name in Object.keys(Game.spawns):
            ResourcePlanner._run_spawn(Game.spawns[name])

    @staticmethod
    def _run_spawn(spawn):
        ResourcePlanner._load_memory(spawn.room)
        ResourcePlanner._scrub_memory(spawn)

    @staticmethod
    def _load_memory(room):
        # ensure this room is listed in memory
        if not Memory.rooms:
            Memory.rooms = {}
        room_mem = Memory.rooms[room.name]
        if not room_mem:
            Memory.rooms[room.name] = {}
        # calculate number of harvesters that can simultaneously
        # harvest each source in this room
        room_resources = room.find(FIND_SOURCES)
        for res in room_resources:
            if not Memory.rooms[room.name]['resources']:
                Memory.rooms[room.name]['resources'] = {}
            resource = room_mem['resources'][res.id]
            if not resource:
                Memory.rooms[room.name]['resources'][res.id] = {}
            if resource['harvest_spots']:
                wall_found = 0
                for x in range(-1, 2):
                    for y in range(-1, 2):
                        if room.getPositionAt(res.pos.x + x,
                                     res.pos.y + y).lookFor(LOOK_TERRAIN) == 'wall':
                            wall_found += 1
                Memory.rooms[room.name]['resources'][res.id]['harvest_spots'] = 9 - wall_found
                if not Memory.rooms[room.name]['resources'][res.id]['miners']:
                    Memory.rooms[room.name]['resources'][res.id]['miners'] = []

    @staticmethod
    def _scrub_memory(spawn):
        for creep_name in Object.keys(Memory.creeps):
            source = Memory.creeps[creep_name].source
            role = Memory.creeps[creep_name].role
            # if creep dead
            if source:
                if role == MINER:
                    if not Object.keys(Game.creeps).includes(creep_name):
                                if not Memory.rooms[spawn.room.name]['resources'][source]['miners']:
                                    Memory.rooms[spawn.room.name]['resources'][source]['miners'] = []
                    # if creep alive
                    else:
                        miners_on_source = len(Memory.rooms[spawn.room.name]['resources'][source]['miners'])
                        harvest_spots = Memory.rooms[spawn.room.name]['resources'][source]['harvest_spots']
                        if miners_on_source > harvest_spots:
                            del Memory.creeps[creep_name].source
                            Memory.rooms[spawn.room.name]['resources'][source]['miners'].pop(creep_name)

