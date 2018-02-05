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


class RemoteDefender(Soldier):
    role = 'remote_defender'

    body_composition = [
        [TOUGH, TOUGH, TOUGH, TOUGH, TOUGH,
         ATTACK, ATTACK, ATTACK, ATTACK, ATTACK,
         MOVE, MOVE, MOVE, MOVE, MOVE]
    ]

    def run_creep(self):
        target = self._get_target()
        if target:
            self.creep.moveTo(target)
            self.creep.attack(target)

    def _get_target(self):
        target = Game.getObjectById(self.creep.memory.target)
        if not target:
            if self.creep.memory.room == self.creep.room:
                hostiles = self.creep.room.find(FIND_HOSTILE_CREEPS)
                if hostiles:
                    target = self.get_closest_to_creep(
                        hostiles
                    )
        if target:
            self.creep.memory.target = target.id
            return target


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