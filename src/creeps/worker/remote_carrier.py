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

class RemoteCarrier(Worker):
    role = 'remote_carrier'
    body_composition = [
        [CARRY, CARRY, CARRY, CARRY, CARRY,
         CARRY, CARRY, CARRY, CARRY, CARRY,
         CARRY, CARRY, CARRY, CARRY, CARRY,
         CARRY, CARRY, CARRY,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE, MOVE],
    ]

    def run_creep(self):
        if _.sum(self.creep.carry) < self.creep.carryCapacity:
            if self.creep.room.name != self.creep.memory.room:
                # if not find a route to there
                exit_dir = self.creep.room.findExitTo(self.creep.memory.room)
                if exit_dir:
                    room_exit = self.creep.pos.findClosestByRange(exit_dir)
                    if room_exit:
                        self.creep.moveTo(room_exit)

    def _get_source(self):
        pass

    def _get_target(self):
        pass
