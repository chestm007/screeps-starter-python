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
        self.towers = Game.rooms[self.room].find(FIND_MY_STRUCTURES).filter(
            lambda s: s.structureType == STRUCTURE_TOWER
        )

        self.damaged_structures = Game.rooms[self.room].find(FIND_STRUCTURES).filter(
            lambda s: s.hits < s.hitsMax
        )

    def run_towers(self):
        for tower in self.towers:
            if len(self.damaged_structures) > 0:
                tower.repair(self.damaged_structures[0])
