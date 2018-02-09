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


class Kiter(Soldier):
    role = 'kiter'

    body_composition = [[TOUGH, TOUGH, TOUGH, TOUGH, TOUGH,
                         TOUGH, TOUGH, TOUGH, TOUGH, TOUGH,
                         RANGED_ATTACK, RANGED_ATTACK, RANGED_ATTACK, RANGED_ATTACK, RANGED_ATTACK,
                         MOVE, MOVE, MOVE, MOVE, MOVE,
                         MOVE, MOVE, MOVE, MOVE, MOVE,
                         MOVE, MOVE, MOVE, MOVE, MOVE]]

    def run_creep(self):

        flag = Game.flags[self.creep.memory.flag]
        if flag:
            if self.creep.room.name != flag.pos.roomName:
                exit_dir = self.creep.room.findExitTo(flag.pos.roomName)
                if exit_dir:
                    room_exit = self.creep.pos.findClosestByRange(exit_dir)
                    if room_exit:
                        self.creep.moveTo(room_exit, {'maxRooms': 1,
                                                      'ignoreCreeps': True})
            else:
                target = self._get_target()
                if target:
                    self.creep.moveTo(target, {'range': 3})
                    self.creep.rangedAttack(target)
                else:
                    self.creep.moveTo(flag, {'ignoreCreeps': True,
                                             'maxRooms': 1})

    def _get_target(self):
        target = Game.flags['attack']
        if not target:
            target = Game.getObjectById(self.creep.memory.target)
            if not target:
                    target = self.creep.pos.findClosestByRange(FIND_HOSTILE_CREEPS)

                    if target:
                        self.creep.memory.target = target.id
        return target
