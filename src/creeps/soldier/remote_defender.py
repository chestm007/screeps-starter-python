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


class RemoteDefender(Soldier):
    role = 'remote_defender'

    body_composition = [
        [TOUGH, TOUGH, TOUGH, TOUGH, TOUGH,
         ATTACK, ATTACK, ATTACK, ATTACK, ATTACK,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         ]
    ]

    def run_creep(self):
        if self.creep.room.name != self.creep.memory.room:
            exit_dir = self.creep.room.findExitTo(self.creep.memory.room)
            if exit_dir:
                room_exit = self.creep.pos.findClosestByRange(exit_dir)
                if room_exit:
                    self.creep.moveTo(room_exit)
        else:
            target = self._get_target()
            if target:
                self.creep.moveTo(target)
                self.creep.attack(target)
            else:
                controller = self.creep.room.controller
                if controller:
                    self.creep.moveTo(controller)

    def _get_target(self):
        target = Game.getObjectById(self.creep.memory.target)
        if not target:
            if Game.time % 3 == 0:
                if self.creep.memory.room == self.creep.room.name:
                    target = self.creep.pos.findClosestByRange(FIND_HOSTILE_CREEPS)
                    if target:
                        self.creep.memory.target = target.id

        return target