from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class Cache:
    def __init__(self):
        self.rooms = {}

    def add_room_to_cache(self, room):
            self.rooms[room.name] = RoomCache(room)

    def get_room_cache(self, room):
        return self.rooms[room.name]


class RoomCache:
    def __init__(self, room: Room):
        self.room = room
        self.structures = None
        self.construction_sites = None
        self.resources = None
        self.dropped_resources = None

    def get_structures(self):
        if self.structures is None:
            self.structures = self.room.find(FIND_STRUCTURES)
        return self.structures

    def get_construction_sites(self):
        if self.construction_sites is None:
            self.construction_sites = self.room.find(FIND_CONSTRUCTION_SITES)
        return self.construction_sites

    def get_resources(self):
        if self.resources is None:
            self.resources = self.room.find(FIND_SOURCES)
        return self.resources

    def get_dropped_resources(self):
        if self.dropped_resources is None:
            self.dropped_resources = self.room.find(FIND_DROPPED_RESOURCES)
        return self.dropped_resources
