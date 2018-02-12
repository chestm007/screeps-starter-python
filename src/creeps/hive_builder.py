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


class HiveBuilder(Worker):
    role = 'hive_builder'

    body_composition = [
        [WORK, WORK,
         CARRY, CARRY, CARRY, CARRY,
         MOVE, MOVE, MOVE],
        [WORK, WORK, WORK, WORK, WORK,
         CARRY, CARRY, CARRY, CARRY, CARRY,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         ]
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
            self._pre_run_checks()
            if self.creep.memory.filling:
                self._harvest_source(self._get_source())

            else:
                s = self.creep.memory.target
                struct = None
                if s:
                    struct = Game.getObjectById(s)
                if not struct:
                    structs = self.creep.room.find(FIND_CONSTRUCTION_SITES)
                    if structs:
                        struct = _(structs).sample()
                        if struct:
                            self.creep.memory.target = struct.id
                if struct:
                    self.creep.build(struct)
                    self.creep.moveTo(struct)
        else:
            if flag:
                self.creep.moveTo(flag)
