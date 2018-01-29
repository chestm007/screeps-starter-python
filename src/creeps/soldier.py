from creeps.creeps import Creeps
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class Soldier(Creeps):
    role = 'soldier'


class RangedSoldier(Soldier):
    pass


class CombatSoldier(Soldier):
    @staticmethod
    def run_creep(creep):
        hostile = _(Game.rooms.find(FIND_HOSTILE_CREEPS)).sample()
    pass