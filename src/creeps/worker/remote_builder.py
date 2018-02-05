from creeps.worker.worker import Worker
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

class RemoteBuilder(Worker):
    role = 'remote_builder'

    body_composition = [
        [WORK,
         CARRY, CARRY, CARRY, CARRY,
         MOVE, MOVE, MOVE, MOVE],
    ]

    def run_creep(self):
        if self.creep.carry[RESOURCE_ENERGY] >= self.creep.carryCapacity:
            self.creep.memory.filling = False
        elif self.creep.carry[RESOURCE_ENERGY] <= 0:
            self.creep.memory.filling = True
        if self.creep.memory.filling:
            source = self._get_source()
            if source:
                self.creep.moveTo(source)
                self.creep.withdraw(source, RESOURCE_ENERGY)
                self.creep.harvest(source)
        else:
            if self.creep.room.name != self.creep.memory.room:
                # if not find a route to there
                exit_dir = self.creep.room.findExitTo(self.creep.memory.room)
                if exit_dir:
                    room_exit = self.creep.pos.findClosestByRange(exit_dir)
                    if room_exit:
                        self.creep.moveTo(room_exit)
            else:
                target = self._get_target()
                if target:
                    res = self.creep.build(target)
                    if res == ERR_INVALID_TARGET:
                        res = self.creep.repair(target)
                    if res == ERR_NOT_IN_RANGE:
                        self.creep.moveTo(target)
                        self.creep.build(target)
                    if target.hits:
                        if target.hits >= target.hitsMax:
                            del self.creep.memory.target

    def _get_source(self):
        pass

    def _get_target(self):
        pass
