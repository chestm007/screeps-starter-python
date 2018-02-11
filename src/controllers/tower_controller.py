from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class TowerController:
    def __init__(self, room):
        self.room = room
        settings = Memory.rooms[self.room].settings
        if not settings:
            Memory.rooms[self.room].settings = {}
        self.max_wall_hits = Memory.rooms[room].settings.max_wall_hits
        if not self.max_wall_hits:
            self.max_wall_hits = 30000
        self.max_rampart_hits = Memory.rooms[room].settings.max_rampart_hits
        if not self.max_rampart_hits:
            self.max_rampart_hits = 30000

        self.settings = None
        self.towers = []
        if Game.rooms[self.room]:
            self.towers = Game.rooms[self.room].find(FIND_MY_STRUCTURES).filter(
                lambda s: s.structureType == STRUCTURE_TOWER
            )

            self.all_structures = Game.rooms[self.room].find(FIND_STRUCTURES)
            self.damaged_structures = self.all_structures.filter(
                lambda s: s.hits < s.hitsMax
                and s.structureType != STRUCTURE_WALL
                and s.structureType != STRUCTURE_RAMPART

            )
            self.almost_dead_borders = self.all_structures.filter(
                lambda s: (s.structureType == STRUCTURE_WALL or s.structureType == STRUCTURE_RAMPART)
                and s.hits < 100
            )
            self.damaged_walls = self.all_structures.filter(
                lambda s: s.structureType == STRUCTURE_WALL and s.hits < self.max_wall_hits
            )
            self.damaged_ramparts = self.all_structures.filter(
                lambda s: s.structureType == STRUCTURE_RAMPART and s.hits < self.max_rampart_hits
            )
            self.hostile_creeps = Game.rooms[self.room].find(FIND_HOSTILE_CREEPS)

    def run_towers(self):
        for tower in self.towers:
            if len(self.almost_dead_borders) > 0:
                tower.repair(self.almost_dead_borders[0])
            elif len(self.hostile_creeps) > 0:
                tower.attack(self.hostile_creeps[0])
            elif len(self.damaged_structures) > 0:
                tower.repair(self.damaged_structures[0])
            elif len(self.damaged_walls) > 0:
                tower.repair(self.damaged_walls[0])
            elif len(self.damaged_ramparts) > 0:
                tower.repair(self.damaged_ramparts[0])
