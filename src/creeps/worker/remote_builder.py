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
        [WORK, WORK,
         CARRY, CARRY, CARRY, CARRY, CARRY, CARRY,
         MOVE, MOVE, MOVE, MOVE],
    ]

    def run_creep(self):
        if self.creep.room.name != self.creep.memory.room:
            # if not find a route to there
            exit_dir = self.creep.room.findExitTo(self.creep.memory.room)
            if exit_dir:
                room_exit = self.creep.pos.findClosestByRange(exit_dir)
                if room_exit:
                    self.creep.moveTo(room_exit)
        else:
            if self.creep.carry[RESOURCE_ENERGY] >= self.creep.carryCapacity:
                self.creep.memory.filling = False
                del self.creep.memory.source
            elif self.creep.carry[RESOURCE_ENERGY] <= 0:
                self.creep.memory.filling = True
            if self.creep.memory.filling:
                source = self._get_source()
                if source:
                    self.creep.moveTo(source)
                    self.creep.pickup(source)
            else:
                target = self._get_target()
                if target:
                    if target.hits:
                        self.creep.repair(target)
                        if target.hits >= target.hitsMax:
                            del self.creep.memory.target
                    else:
                        self.creep.build(target)
                    self.creep.moveTo(target)

    def _get_source(self):
        res = self.creep.pos.findClosestByRange(FIND_DROPPED_RESOURCES)
        if res:
            self.creep.memory.source = res.id
        return res

    def _get_target(self):
        target = None
        if self.creep.memory.target:
            target = Game.getObjectById(self.creep.memory.target)
        if not target:
            target = self.get_closest_to_creep(
                self.structures_in_room.filter(lambda s: s.hits < s.hitsMax / 2)
            )
            if not target:
                target = self.get_closest_to_creep(
                    self.construction_sites_in_room.filter(
                        lambda s: s.structureType == STRUCTURE_SPAWN
                    )
                )
            if not target:
                target = self.creep.pos.findClosestByRange(FIND_CONSTRUCTION_SITES)
            if target:
                self.creep.memory.target = target.id
        return target
