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
ROOM_HEIGHT = 50
ROOM_WIDTH = 50


class Worker(Creeps):
    role = 'harvester'

    body_composition = {
        'small': [WORK, CARRY, MOVE, MOVE],
        'medium': [WORK, WORK, CARRY, MOVE, MOVE, MOVE],
        'large': [WORK, WORK, WORK, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE],
        'xlarge': [WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE]
    }

    @staticmethod
    def factory(spawn):
        body = None
        for size in ['small', 'medium', 'large', 'xlarge']:
            if spawn.room.energyAvailable >= Worker._calculate_creation_cost(Worker.body_composition[size]):
                body = Worker.body_composition[size]
        console.log('spawning new {} worker creep'.format(body))
        Creeps.create(body, spawn, Harvester.role)

    @staticmethod
    def _pre_run_checks(creep):
        if Worker._is_creep_empty(creep):
            Worker.creep_empty(creep)
        elif Worker._is_creep_full(creep):
            Worker.creep_full(creep)
        if not creep.memory.filling:
            creep.memory.filling = False

    @staticmethod
    def _get_num_harvesters():
        return len([Game.creeps[name] for name in Object.keys(Game.creeps)
                    if str(Game.creeps[name].memory.role) == Harvester.role])

    @staticmethod
    def _should_be_builder(creep):
        if Worker._get_num_harvesters() >= MAX_HARVESTERS:
            if creep.room.find(FIND_CONSTRUCTION_SITES):
                return True

    @staticmethod
    def _should_be_harvester(creep):
        if creep.room.find(FIND_CONSTRUCTION_SITES):
            if Worker._get_num_harvesters() < MIN_HARVESTERS:
                return True
        else:
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

    @staticmethod
    def get_closest_to_creep(creep, obj_list):
        least_distance = 1000
        for r in obj_list:
            distance_to_creep = r.pos.getRangeTo(creep.pos)
            if distance_to_creep < least_distance:
                least_distance = distance_to_creep
                closest = r
        return closest


class Builder(Worker):
    role = 'builder'

    @staticmethod
    def run_creep(creep):
        if Builder._should_be_harvester(creep):
            Builder._become_harvester(creep)
            console.log('{} is becoming a harvester'.format(creep.name))
            Harvester.run_creep(creep)
            return

        Worker._pre_run_checks(creep)

        if creep.memory.filling:
            Builder.move_to_and_harvest(creep)
            return
        else:
            target = Builder._get_target(creep)
            if target:
                target_obj = Game.getObjectById(creep.memory.target)
                if target_obj.structureType == STRUCTURE_ROAD:
                    if target_obj.hits >= target_obj.hitsMax / 3 * 2:
                        del creep.memory.target
                        Builder._get_target(creep)
                    res = creep.repair(target)
                    if res == ERR_NOT_IN_RANGE:
                        creep.moveTo(target)
                        return
                    elif res == OK:
                        return
                res = creep.build(target)
                if res == ERR_NOT_IN_RANGE:
                    creep.moveTo(target)
                    return
                elif res == OK:
                    return
            del creep.memory.target

    @staticmethod
    def _get_target(creep):
        if creep.memory.target:
            target = Game.getObjectById(creep.memory.target)
        else:
            structures_in_room = creep.room.find(FIND_STRUCTURES)
            if creep.memory.source:
                target = Worker.get_closest_to_creep(
                    creep,
                    structures_in_room.filter(
                        lambda s: s.hits < s.hitsMax / 2 and
                                  s.pos.getRangeTo(Game.getObjectById(creep.memory.source).pos) < ROOM_HEIGHT / 2
                    )
                )
            if not target:
                construction_sites = creep.room.find(FIND_CONSTRUCTION_SITES)
                target = Worker.get_closest_to_creep(
                    creep,
                    construction_sites.filter(
                        lambda s: s.structureType == STRUCTURE_ROAD
                    )
                )
                if not target:
                    target = creep.pos.findClosestByRange(FIND_CONSTRUCTION_SITES)
            if target:
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
        if Harvester._should_be_builder(creep):
            Harvester._become_builder(creep)
            Builder.run_creep(creep)
            return

        Worker._pre_run_checks(creep)

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
            structures_in_room = creep.room.find(FIND_STRUCTURES)
            # fill extentions and spawns first
            target = Worker.get_closest_to_creep(
                creep,
                structures_in_room.filter(
                    lambda s: (s.structureType == STRUCTURE_EXTENSION or s.structureType == STRUCTURE_SPAWN)
                              and s.energy < s.energyCapacity
            ))
            if not target:
                # Get a random new target.
                target = _(structures_in_room).filter(lambda s: s.structureType == STRUCTURE_CONTROLLER).sample()
            if target:
                creep.memory.target = target.id
        return target
