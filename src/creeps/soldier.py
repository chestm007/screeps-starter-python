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

    body_composition = {
        'large': [TOUGH, TOUGH, TOUGH, TOUGH, TOUGH,
                  ATTACK, ATTACK, ATTACK, ATTACK, ATTACK,
                  MOVE, MOVE, MOVE, MOVE, MOVE]
    }

    @staticmethod
    def factory(spawn, num_workers):
        size = 'large'
        if spawn.room.energyAvailable >= RemoteDefender._calculate_creation_cost(RemoteDefender.body_composition[size]):
            body = RemoteDefender.body_composition[size]

            console.log('spawning new {} {} creep'.format(size, RemoteDefender.__name__))
            Creeps.create(body, spawn, RemoteDefender.role)

    def run_creep(self):
        target = self._get_target()
        if target:
            self.creep.moveTo(target)
            self.creep.attack(target)

    def _get_target(self):
        target = Game.getObjectById(self.creep.memory.target)
        if not target:
            if self.creep.memory.flag:
                flag = Game.flags[self.creep.memory.flag.replace('Spawn', '')]
            if not flag:
                worked_flags = [Memory.creeps[creep].flag for creep in Object.keys(Game.creeps)
                                if Memory.creeps[creep].role == 'remote_defender']

                flags = Object.keys(Game.flags).filter(
                    lambda f: not worked_flags.includes(f)
                                 and (
                                  str(f).startswith('reserve')
                                  or str(f).startswith('claim')
                              ) and not str(f).endswith('Spawn')
                )
                if len(flags) > 0:
                    flag = Game.flags[flags[0]]
                    self.creep.memory.flag = flag.name
            if flag:
                if flag.room == self.creep.room:
                    hostiles = self.creep.room.find(FIND_HOSTILE_CREEPS)
                    if hostiles:
                        target = self.get_closest_to_creep(
                            hostiles
                        )
        if target:
            self.creep.memory.target = target.id
            return target
        elif flag:
            return flag

class Sumo(Soldier):
    role = 'sumo'
    body_composition = {
        'large': [MOVE, MOVE, MOVE, MOVE, MOVE,
                  MOVE, MOVE, MOVE, MOVE, MOVE,
                  MOVE, MOVE, MOVE, MOVE, MOVE,
                  HEAL, HEAL, HEAL, HEAL, HEAL,
                  HEAL, HEAL, HEAL, HEAL, HEAL,
                  HEAL, HEAL, HEAL, HEAL, HEAL,
                  ATTACK, ATTACK, ATTACK, ATTACK, ATTACK]
    }
    @staticmethod
    def factory(spawn, num_workers):
        size = 'large'
        console.log('attempting')
        if spawn.room.energyAvailable >= RemoteDefender._calculate_creation_cost(RemoteDefender.body_composition[size]):
            body = RemoteDefender.body_composition[size]

            console.log('spawning new {} {} creep'.format(size, RemoteDefender.__name__))
            Creeps.create(body, spawn, RemoteDefender.role)

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