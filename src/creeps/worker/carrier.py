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


class Carrier(Worker):
    role = 'carrier'
    body_composition = [
        [CARRY, CARRY,
         MOVE, MOVE],
        [CARRY, CARRY, CARRY, CARRY,
         MOVE, MOVE, MOVE, MOVE],
        [CARRY, CARRY, CARRY, CARRY, CARRY,
         CARRY, CARRY, CARRY, CARRY, CARRY,
         CARRY, CARRY, CARRY,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE],
        [CARRY, CARRY, CARRY, CARRY, CARRY,
         CARRY, CARRY, CARRY, CARRY, CARRY,
         CARRY, CARRY, CARRY, CARRY, CARRY,
         CARRY, CARRY, CARRY, CARRY, CARRY,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE, MOVE, MOVE]
    ]

    def run_creep(self):
        source = None
        if _.sum(self.creep.carry) <= 0:
            self.creep.memory.filling = True
        elif _.sum(self.creep.carry) >= self.creep.carryCapacity:
            self.creep.memory.filling = False
            del self.creep.memory.source
        if self.creep.memory.source:
            source = Game.getObjectById(self.creep.memory.source)
            if source and source.structureType == STRUCTURE_STORAGE:
                del self.creep.memory.source
        else:
            source = _(self.dropped_resources_in_room.filter(
                lambda r: r.resourceType == RESOURCE_ENERGY and r.amount >= 100
            )).sample()
            if not source:
                miner_containers = [
                    Game.getObjectById(Memory.creeps[miner].source_container)
                    for miner in Object.keys(Game.creeps)
                    if Memory.creeps[miner].role == 'miner' and Game.creeps[miner].room == self.creep.room]

                miner_containers = [
                    container for container in miner_containers
                    if container
                    and container.store[RESOURCE_ENERGY] > self.creep.carryCapacity * 1.3]

            if source:
                self.creep.memory.source = source.id
            if miner_containers:
                source = reversed(sorted(miner_containers, lambda c: c.store[RESOURCE_ENERGY]))[0]
                if source:
                    self.creep.memory.source = source.id
            if not source:
                source = self.creep.room.storage
                if source:
                    self.creep.memory.source = source.id
        if self.creep.memory.filling:
            if source:
                dropped_energy = source.pos.lookFor(RESOURCE_ENERGY)
                if len(dropped_energy) > 0:
                    self.creep.moveTo(source)
                    self.creep.pickup(dropped_energy[0])
            self._harvest_source(source)
        else:
            target = self._get_target()
            res = self.creep.transfer(target, RESOURCE_ENERGY)
            if res == OK:
                del self.creep.memory.target
            elif res == ERR_NOT_IN_RANGE:
                if len(self.creep.pos.findInRange(STRUCTURE_EXTENSION, 5)) > 0:
                    result = self.creep.moveTo(target, {'ignoreCreeps': True})
                else:
                    result = self.creep.moveTo(target)
            elif res == ERR_FULL:
                del self.creep.memory.target
            elif res == ERR_INVALID_TARGET:
                del self.creep.memory.target
            else:
                console.log("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                    self.creep.name, target, RESOURCE_ENERGY, res))
                del self.creep.memory.target

    def _get_target(self):
        if self.creep.memory.target:
            return Game.getObjectById(self.creep.memory.target)

        target = self.get_closest_to_creep(
            self.structures_in_room.filter(
                lambda s: s.structureType == STRUCTURE_TOWER
                          and s.energy < 100
            )
        )
        if target:
            self.creep.memory.target = target.id
            return target
        target = self.get_closest_to_creep(
            self.structures_in_room.filter(
                lambda s: (
                              s.structureType == STRUCTURE_EXTENSION
                              or s.structureType == STRUCTURE_SPAWN
                          ) and s.energy < s.energyCapacity
            ))
        if target:
            self.creep.memory.target = target.id
            return target

        target = self.get_closest_to_creep(
            self.structures_in_room.filter(
                lambda s: s.structureType == STRUCTURE_TOWER
                          and s.energy < s.energyCapacity * 0.7
            )
        )
        if target:
            self.creep.memory.target = target.id
            return target

        containers = [Memory.creeps[creep].source_container for creep in Object.keys(Game.creeps)]
        unmined_containers = self.structures_in_room.filter(
            lambda s: (s.structureType == STRUCTURE_CONTAINER or s.structureType == STRUCTURE_STORAGE)
                       and not containers.includes(s.id) and s.store[RESOURCE_ENERGY] < s.storeCapacity*0.7
        )
        if unmined_containers:
            target = sorted(unmined_containers,
                            lambda c: c.storeCapacity / c.store[RESOURCE_ENERGY]
                            and c.store[RESOURCE_ENERGY] < c.storeCapacity * 0.9)[0]
            if target:
                self.creep.memory.target = target.id
                return target

        target = Game.creeps[self.creep.name].room.storage
        if target:
            self.creep.memory.target = target.id
            return target