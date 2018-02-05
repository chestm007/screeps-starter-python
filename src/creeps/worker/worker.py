from creeps.creeps import Creeps
from creeps.worker.claimer import Claimer
from creeps.worker.harvester import Harvester
from creeps.worker.builder import Builder
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


MAX_HARVESTERS = 4
MIN_HARVESTERS = 3
ROOM_HEIGHT = 50
ROOM_WIDTH = 50


class Worker(Creeps):
    role = 'harvester'

    body_composition = [
        [WORK,
         CARRY,
         MOVE, MOVE],
        [WORK, WORK,
         CARRY,
         MOVE, MOVE],
        [WORK, WORK, WORK,
         CARRY, CARRY,
         MOVE, MOVE, MOVE],
        [WORK, WORK, WORK, WORK, WORK,
          WORK, WORK,
         CARRY, CARRY,
         MOVE, MOVE, MOVE, MOVE]
    ]

    def _pre_run_checks(self):
        if self._is_creep_empty():
            self.creep_empty()
        elif self._is_creep_full():
            self.creep_full()
        if not self.creep.memory.filling:
            self.creep.memory.filling = False

    def _get_num_harvesters(self):
        return len([Game.creeps[name] for name in Object.keys(Game.creeps)
                    if str(Game.creeps[name].memory.role) == Harvester.role
                    and Game.creeps[name].room == self.creep.room])

    def _should_be_builder(self):
        if self._get_num_harvesters() >= 2:
            if len(self.construction_sites_in_room) > 0:
                return 'construction sites exist'
            if self.creep.memory.source:
                target = self.get_closest_to_creep(
                    self.structures_in_room.filter(
                        lambda s: s.hits < s.hitsMax / 2
                        and s.structureType != STRUCTURE_RAMPART
                        and s.structureType != STRUCTURE_WALL
                    )
                )
                if target:
                    self.creep.memory.target = target.id
                    return 'structures need repair {}'.format(target.structureType)
            claimers = [Game.creeps[creep] for creep in Object.keys(Game.creeps)
                        if Game.creeps[creep].memory.role == Claimer.role]

            for claimer in claimers:
                unbuilt_spawn = _(claimer.room.find(FIND_CONSTRUCTION_SITES).filter(
                    lambda s: s.structureType == STRUCTURE_SPAWN
                )).sample()
                if unbuilt_spawn:
                    return True

    def _should_be_harvester(self):
        if self._get_num_harvesters() < 1:
            return 'not enough harvesters'
        else:
            if self.creep.memory.source:
                target = self.get_closest_to_creep(
                    self.structures_in_room.filter(
                        lambda s: s.hits < s.hitsMax / 2
                        and s.structureType != STRUCTURE_WALL
                        and s.structureType != STRUCTURE_RAMPART
                    )
                )
                if target:
                    self.creep.memory.target = target.id
                    return False
            claimers = [Game.creeps[creep] for creep in Object.keys(Game.creeps)
                        if Game.creeps[creep].memory.role == Claimer.role]

            for claimer in claimers:
                unbuilt_spawn = _(claimer.room.find(FIND_CONSTRUCTION_SITES).filter(
                    lambda s: s.structureType == STRUCTURE_SPAWN
                )).sample()
                if unbuilt_spawn:
                    return False
            if len(self.construction_sites_in_room) <= 0:
                return 'no construction sites'

    def _become_builder(self):
        self.creep.memory.role = Builder.role
        del self.creep.memory.target

    def _become_harvester(self):
        self.creep.memory.role = Harvester.role
        del self.creep.memory.target

    def _get_source(self):
        source = None
        if self.creep.memory.source:
            source = Game.getObjectById(self.creep.memory.source)
            if source:
                if source.energyCapacity:
                    if source.energy <= 0:
                        del self.creep.memory.source
        if not source:
            containers = [Memory.creeps[creep].source_container for creep in Object.keys(Game.creeps)]
            source = self.get_closest_to_creep(
                self.structures_in_room.filter(
                    lambda s: (s.structureType == STRUCTURE_CONTAINER or s.structureType == STRUCTURE_STORAGE)
                    and not containers.includes(s.id)
                    and s.store[RESOURCE_ENERGY] > self.creep.carryCapacity * 2
                ))
            if source:
                self.creep.memory.source = source.id
        if not source:
            source = _(self.dropped_resources_in_room.filter(
                lambda r: r.resourceType == RESOURCE_ENERGY
            )).sample()
        if source:
            self.creep.memory.source = source.id
        if not source:
            if self.creep.room.storage:
                source = self.creep.room.storage
                self.creep.memory.source = source.id
            if not source:
                source = self.get_closest_to_creep(
                    self.structures_in_room.filter(
                        lambda s: s.structureType == STRUCTURE_CONTAINER
                        and s.store[RESOURCE_ENERGY] > self.creep.carryCapacity
                    ))
            if not source:
                # Get a random new source and save it
                source = _(self.creep.room.find(FIND_SOURCES).filter(
                    lambda s: s.energy > 0
                )).sample()
                if source:
                    self.creep.memory.source = source.id
        return source

    def _harvest_source(self, source):
        if not source:
            del self.creep.memory.source
            return
        if source.structureType == STRUCTURE_CONTAINER or source.structureType == STRUCTURE_STORAGE:
            res = self.creep.withdraw(source, RESOURCE_ENERGY)
            if res == ERR_NOT_IN_RANGE:
                self.creep.moveTo(source)
            elif res == ERR_NOT_ENOUGH_ENERGY or ERR_NOT_ENOUGH_RESOURCES:
                del self.creep.memory.source
                self._get_source()
        else:
            if source.resourceType == RESOURCE_ENERGY:
                res = self.creep.pickup(source)
                if res == ERR_NOT_IN_RANGE:
                    self.creep.moveTo(source)
                elif res == ERR_NOT_ENOUGH_ENERGY:
                    del self.creep.memory.source
                    self._get_source()
                elif res == ERR_BUSY:
                    pass
                elif res != OK:
                    console.log('{} cannot withdraw from {} {}'
                                .format(self.creep.memory.role, source.structureType, res))
                return res

            # If we're near the source, harvest it - otherwise, move to it.
            else:
                result = self.creep.harvest(source)
                if result == ERR_NOT_IN_RANGE:
                    self.creep.moveTo(source)
                elif result == ERR_NOT_ENOUGH_ENERGY:
                    return
                elif result != OK:
                    console.log("[{}] Unknown result from creep.harvest({}): {}"
                                .format(self.creep.name, source, result))
                    del self.creep.memory.source
                return result

    def _transfer_energy(self, target):
        if self._is_close_to_target(target):
            # If we are targeting a spawn or extension, transfer energy. Otherwise, use upgradeController on it.
            if target.energyCapacity:
                self._transfer_energy_to_target(target)
            else:
                self._upgrade_controller(target)
        else:
            self.creep.moveTo(target)

    def _upgrade_controller(self, target):
        self.creep.upgradeController(target)
        if not self.creep.pos.inRangeTo(target, 2):
            self.creep.moveTo(target)

    def _transfer_energy_to_target(self, target):
        result = self.creep.transfer(target, RESOURCE_ENERGY)
        if result == OK:
            del self.creep.memory.target
        elif result == ERR_NOT_IN_RANGE:
            self.creep.moveTo(target)
        elif result == ERR_FULL:
            del self.creep.memory.target
        elif result == ERR_INVALID_TARGET:
            del self.creep.memory.target
        else:
            console.log("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                self.creep.name, target, RESOURCE_ENERGY, result))
            del self.creep.memory.target
        return result

    def _is_close_to_target(self, target):
        # If we are targeting a spawn or extension, we need to be directly next to it - otherwise, we can be 3 away.
        if target:
            if target.energyCapacity:
                return self.creep.pos.isNearTo(target)
            else:
                return self.creep.pos.inRangeTo(target, 3)

    def creep_empty(self):
        self.creep.memory.filling = True
        del self.creep.memory.target

    def creep_full(self):
        self.creep.memory.filling = False
        del self.creep.memory.source

    def _is_creep_full(self):
        # If we're full, stop filling up and remove the saved source
        if self.creep.memory.filling and _.sum(self.creep.carry) >= self.creep.carryCapacity:
            return True

    def _is_creep_empty(self):
        # If we're empty, start filling again and remove the saved target
        if not self.creep.memory.filling and self.creep.carry.energy <= 0:
            return True

    def _get_target(self) -> RoomObject:
        pass


