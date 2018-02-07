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
         MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE],
    ]

    def run_creep(self):
        if _.sum(self.creep.carry) < self.creep.carryCapacity:
            if self.creep.room.name != self.creep.memory.room:
                # if not find a route to there
                exit_dir = self.creep.room.findExitTo(self.creep.memory.room)
                if exit_dir:
                    room_exit = self.creep.pos.findClosestByRange(exit_dir)
                    if room_exit:
                        self.creep.moveTo(room_exit, {'maxRooms': 1})
            else:
                resources = None
                res = self.creep.memory.resources
                if res:
                    resources = Game.getObjectById(res)
                if not resources:
                    src = self.creep.memory.source
                    if src:
                        source = Game.getObjectById(src)
                        if source:
                            resources = source.pos.findClosestByRange(FIND_DROPPED_RESOURCES)
                            if resources:
                                self.creep.memory.resources = resources.id
                if resources:
                    self.creep.moveTo(resources, {'maxRooms': 1})
                    self.creep.pickup(resources)
                else:
                    src = self.creep.memory.source
                    if src:
                        source = Game.getObjectById(src)
                        if source:
                            self.creep.moveTo(source, {'maxRooms': 1,
                                                       'range': 4})
        else:
            if self.creep.room.name != self.creep.memory.hive:
                exit_dir = self.creep.room.findExitTo(self.creep.memory.hive)
                if exit_dir:
                    room_exit = self.creep.pos.findClosestByRange(exit_dir)
                    if room_exit:
                        self.creep.moveTo(room_exit, {'maxRooms': 1})
            else:
                sto = self.creep.memory.storage
                if sto:
                    storage = Game.getObjectById(sto)
                    if storage:
                        self.creep.moveTo(storage, {'maxRooms': 1})
                        self.creep.transfer(storage, RESOURCE_ENERGY)

    def _get_source(self):
        pass

    def _get_target(self):
        pass
