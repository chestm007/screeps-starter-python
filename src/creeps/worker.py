from creeps.creeps import Creeps
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


class Worker(Creeps):
    role = 'harvester'

    body_composition = {
        'small': [WORK, CARRY, MOVE, MOVE],
        'medium': [WORK, WORK, CARRY, MOVE, MOVE],
        'large': [WORK, WORK, WORK, CARRY, CARRY, MOVE, MOVE]
    }

    @staticmethod
    def factory(spawn):
        if spawn.room.energyAvailable >= 550:
            body = Worker.body_composition['large']
        elif spawn.room.energyAvailable >= 350:
            body = Worker.body_composition['medium']
        else:
            body = Worker.body_composition['small']
        console.log('spawning new worker creep')
        Creeps.create(body, spawn, Builder.role if Worker._should_be_builder() else Harvester.role)

    @staticmethod
    def run_creep(creep):
        if Worker._is_creep_empty(creep):
            Worker.creep_empty(creep)
        elif Worker._is_creep_full(creep):
            Worker.creep_full(creep)
        if not creep.memory.filling:
            creep.memory.filling = False

    @staticmethod
    def _get_num_harvesters():
        return len([Game.creeps[name] for name in Object.keys(Game.creeps) if str(Game.creeps[name].memory.role) == Harvester.role])

    @staticmethod
    def _should_be_builder():
        num_harvesters = Worker._get_num_harvesters()
        if num_harvesters >= MAX_HARVESTERS:
            return True

    @staticmethod
    def _should_be_harvester():
        num_harvesters = Worker._get_num_harvesters()
        if num_harvesters < MIN_HARVESTERS:
            return True

    @staticmethod
    def _become_builder(creep):
        creep.memory.role = Builder.role
        del creep.memory.target

    @staticmethod
    def _become_harvester(creep):
        creep.memory.role = Harvester.role
        del creep.memory.target

    @staticmethod
    def move_to_and_harvest(creep):
        # If we have a saved source, use it
        if creep.memory.source:
            source = Game.getObjectById(creep.memory.source)
        else:
            # Get a random new source and save it
            source = _.sample(creep.room.find(FIND_SOURCES))
            creep.memory.source = source.id

        # If we're near the source, harvest it - otherwise, move to it.
        if creep.pos.isNearTo(source):
            result = creep.harvest(source)
            if result != OK:
                console.log("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, source, result))
                del creep.memory.source
        else:
            creep.moveTo(source)

    @staticmethod
    def creep_empty(creep):
        creep.memory.filling = True
        del creep.memory.target

    @staticmethod
    def creep_full(creep):
        creep.memory.filling = False

    @staticmethod
    def _is_creep_full(creep):
        # If we're full, stop filling up and remove the saved source
        if creep.memory.filling and _.sum(creep.carry) >= creep.carryCapacity:
            return True

    @staticmethod
    def _is_creep_empty(creep):
        # If we're empty, start filling again and remove the saved target
        if not creep.memory.filling and creep.carry.energy <= 0:
            return True


class Builder(Worker):
    role = 'builder'

    @staticmethod
    def run_creep(creep):
        if Builder._should_be_harvester():
            Builder._become_harvester(creep)
            return

        Worker.run_creep(creep)

        if creep.memory.filling:
            Builder.move_to_and_harvest(creep)
            return
        else:
            target = Builder._get_target(creep)
            if target:
                target_obj = Game.getObjectById(creep.memory.target)
                if target_obj.structureType == STRUCTURE_ROAD:
                    if target_obj.hits >= target_obj.maxHits / 2:
                        del creep.memory.target
                        Builder._get_target(creep)
                    if creep.repair(target) == ERR_NOT_IN_RANGE:
                        creep.moveTo(target)
                        return
                if creep.build(target) == ERR_NOT_IN_RANGE:
                    creep.moveTo(target)
                    return
            del creep.memory.target

    @staticmethod
    def _get_target(creep):
        if creep.memory.target:
            target = Game.getObjectById(creep.memory.target)
        else:
            structures_in_room = _(creep.room.find(FIND_STRUCTURES))
            target = structures_in_room.filter(
                lambda s: s.structureType == STRUCTURE_ROAD and s.hits < s.hitsMax / 3
            ).sample()
            if not target:
                target = creep.pos.findClosestByRange(FIND_CONSTRUCTION_SITES)
            creep.memory.target = target.id
        return target


class Harvester(Worker):
    role = 'harvester'

    @staticmethod
    def run_creep(creep):
        """
        Runs a creep as a generic harvester.
        :param creep: The creep to run
        """
        if Harvester._should_be_builder():
            Harvester._become_builder(creep)
            return

        Worker.run_creep(creep)

        if creep.memory.filling:
            Harvester.move_to_and_harvest(creep)
        else:
            target = Harvester._get_target(creep)

            if Harvester._is_close_to_target(creep, target):
                # If we are targeting a spawn or extension, transfer energy. Otherwise, use upgradeController on it.
                if target.energyCapacity:
                    Harvester._transfer_energy_to_target(creep, target)
                else:
                    Harvester._upgrade_controller(creep, target)
            else:
                creep.moveTo(target)

    @staticmethod
    def _upgrade_controller(creep, target):
        result = creep.upgradeController(target)
        if result != OK:
            console.log("[{}] Unknown result from creep.upgradeController({}): {}".format(
                creep.name, target, result))
            del creep.memory.target
        # Let the creeps get a little bit closer than required to the controller, to make room for other creeps.
        if not creep.pos.inRangeTo(target, 2):
            creep.moveTo(target)

    @staticmethod
    def _transfer_energy_to_target(creep, target):
        result = creep.transfer(target, RESOURCE_ENERGY)
        if result == OK or result == ERR_FULL:
            del creep.memory.target
        else:
            console.log("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                creep.name, target, RESOURCE_ENERGY, result))
            del creep.memory.target

    @staticmethod
    def _is_close_to_target(creep, target):
        # If we are targeting a spawn or extension, we need to be directly next to it - otherwise, we can be 3 away.
        if target.energyCapacity:
            return creep.pos.isNearTo(target)
        else:
            return creep.pos.inRangeTo(target, 3)

    @staticmethod
    def _get_target(creep):
        # If we have a saved target, use it
        if creep.memory.target:
            target = Game.getObjectById(creep.memory.target)
        else:
            structures_in_room = _(creep.room.find(FIND_STRUCTURES))
            # fill extentions first
            target = structures_in_room.filter(
                lambda s: s.structureType == STRUCTURE_EXTENSION and s.energy < s.energyCapacit
            ).sample()
            if not target:
                # if spawn has < 250 energy, refill it
                target = structures_in_room.filter(
                    lambda s: s.structureType == STRUCTURE_SPAWN and s.energy < 250
                ).sample()
                if not target:
                    # Get a random new target.
                    target = structures_in_room.filter(
                        lambda s: ((s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_EXTENSION)
                                   and s.energy < s.energyCapacity) or s.structureType == STRUCTURE_CONTROLLER
                    ).sample()
            creep.memory.target = target.id
        return target
