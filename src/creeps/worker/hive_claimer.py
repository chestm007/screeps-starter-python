from creeps.worker.worker import Worker
from defs import *

__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'name')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class HiveClaimer(Worker):
    role = 'hive_claimer'

    body_composition = [
        [CLAIM, MOVE]
    ]

    def run_creep(self):
        flag = None
        f = self.creep.memory.flag
        if f:
            flag = Game.getObjectById(f)
        if not flag:
            claim_flags = [Game.flags[f] for f in Object.keys(Game.flags)
                           if Game.flags[f].name.endswith('hive_claim')]
            if len(claim_flags):
                flag = claim_flags[0]
                if flag:
                    self.creep.memory.flag = flag.id
        if self.creep.room.name == flag.pos.roomName:
            controller = self.creep.room.controller
            if controller:
                self.creep.claimController(controller)
                self.creep.moveTo(controller)
        else:
            if flag:
                self.creep.moveTo(flag)
