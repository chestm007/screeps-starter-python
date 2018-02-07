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


class Sumo(Soldier):
    role = 'sumo'

    body_composition = [
        [TOUGH, TOUGH, TOUGH, TOUGH, TOUGH,
         TOUGH, TOUGH, TOUGH, TOUGH, TOUGH,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         HEAL, HEAL, HEAL, HEAL, HEAL,
         ATTACK, ATTACK, ATTACK, ATTACK, ATTACK]
    ]

    def run_creep(self):
        flag = Game.flags[self.creep.memory.flag]
        if flag:
            if self.creep.room.name != flag.pos.roomName:
                exit_dir = self.creep.room.findExitTo(flag.pos.roomName)
                if exit_dir:
                    room_exit = self.creep.pos.findClosestByRange(exit_dir)
                    if room_exit:
                        damaged_creep = self.creep.pos.findClosestByRange(
                            FIND_MY_CREEPS, {'filter': lambda c: c.hitsMax - c.hits > 200})
                        if damaged_creep:
                            self.creep.heal(damaged_creep)
                            self.creep.rangedHeal(damaged_creep)
                        self.creep.moveTo(room_exit, {'maxRooms': 1,
                                                      'ignoreCreeps': True})
            else:
                if self.creep.hitsMax - self.creep.hits > 200:
                    self.creep.heal(self.creep)
                    self.creep.moveTo(flag, {'ignoreCreeps': True,
                                             'maxRooms': 1})
                else:
                    damaged_creep = self.creep.pos.findClosestByRange(
                        FIND_MY_CREEPS, {'filter': lambda c: c.hitsMax - c.hits > 200})
                    if damaged_creep:
                        self.creep.moveTo(damaged_creep)
                        self.creep.heal(damaged_creep)
                        self.creep.rangedHeal(damaged_creep, {'ignoreCreeps': True,
                                                              'maxRooms': 1})
                    else:
                        target = self._get_target()
                        if target:
                            self.creep.moveTo(target)
                            self.creep.attack(target)
                        else:
                            creep = self.creep.pos.findClosestByRange(FIND_HOSTILE_CREEPS)
                            if creep:
                                self.creep.attack(creep)
                                self.creep.moveTo(creep, {'maxRooms': 1})
                            else:
                                self.creep.moveTo(flag, {'ignoreCreeps': True,
                                                         'maxRooms': 1})

    def _get_target(self):
        target = Game.getObjectById(self.creep.memory.target)
        if not target:
            if Game.time % 3 == 0:
                if self.creep.memory.room == self.creep.room.name:
                    target = self.creep.pos.findClosestByRange(FIND_HOSTILE_CREEPS)
                    if target:
                        self.creep.memory.target = target.id
        return target

