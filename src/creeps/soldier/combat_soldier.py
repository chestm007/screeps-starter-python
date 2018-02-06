from creeps.soldier.soldier import Soldier
from defs import *

__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'name')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class CombatSoldier(Soldier):
    body_composition = {
        'small': [TOUGH, TOUGH, TOUGH, TOUGH, TOUGH,
                  TOUGH, TOUGH, TOUGH, TOUGH, TOUGH,
                  ATTACK,
                  MOVE, MOVE],
        'medium': [TOUGH, TOUGH, TOUGH, TOUGH, TOUGH,
                  TOUGH, TOUGH, TOUGH, TOUGH, TOUGH,
                  ATTACK,
                  MOVE, MOVE],
        'large': [TOUGH, TOUGH, TOUGH, TOUGH, TOUGH,
                  TOUGH, TOUGH, TOUGH, TOUGH, TOUGH,
                  ATTACK,
                  MOVE, MOVE],
        'large': [TOUGH, TOUGH, TOUGH, TOUGH, TOUGH,
                  TOUGH, TOUGH, TOUGH, TOUGH, TOUGH,
                  ATTACK,
                  MOVE, MOVE]
    }
    @staticmethod
    def run_creep(creep):
        hostile = _(Game.rooms.find(FIND_HOSTILE_CREEPS)).sample()
        if creep.attack(hostile) == ERR_NOT_IN_RANGE:
            creep.moveTo(hostile)
    pass