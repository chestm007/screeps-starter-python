from creeps.soldier.soldier import Soldier
from defs import *
from defs import MOVE, HEAL, ATTACK, Game

__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'name')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class Sumo(Soldier):
    role = 'sumo'

    body_composition = [
        [MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         HEAL, HEAL, HEAL, HEAL, HEAL,
         HEAL, HEAL, HEAL, HEAL, HEAL,
         HEAL, HEAL, HEAL, HEAL, HEAL,
         ATTACK, ATTACK, ATTACK, ATTACK, ATTACK]
    ]

    def run_creep(self):
        target = self._get_target()
        if target:
            self.creep.heal(self.creep)
            self.creep.moveTo(target)
            self.creep.attack(target)

    def _get_target(self):
        if self.creep.memory.target:
            target = Game.getObjectById(self.creep.memory.target)
        else:
            target = Game.flags['sumo']
            if target:
                self.creep.memory.target = target.id
        return target