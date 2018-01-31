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
        'small': [WORK,
                  CARRY,
                  MOVE, MOVE],
        'medium': [WORK, WORK,
                   CARRY,
                   MOVE, MOVE],
        'large': [WORK, WORK, WORK,
                  CARRY, CARRY,
                  MOVE, MOVE, MOVE],
        'xlarge': [WORK, WORK, WORK, WORK, WORK,
                   CARRY, CARRY,
                   MOVE, MOVE, MOVE]
    }

    @staticmethod
    def factory(spawn, num_workers):
        body = None
        i = 0
        while True:
            if num_workers >= len(Worker.num_creep_to_size):
                num_workers = len(Worker.num_creep_to_size) - 1
            size = Worker.num_creep_to_size[num_workers - i]
            if not size:
                return
            if spawn.room.energyAvailable >= Worker._calculate_creation_cost(Worker.body_composition[size]):
                body = Worker.body_composition[size]
                break
            i += 1
            if size == 'small':
                break

        console.log('spawning new {} worker creep'.format(size))
        Creeps.create(body, spawn, Worker.role)

    @staticmethod
    def _pre_run_checks(creep):
        if Worker._is_creep_empty(creep):
            Worker.creep_empty(creep)
        elif Worker._is_creep_full(creep):
            Worker.creep_full(creep)
        if not creep.memory.filling:
            creep.memory.filling = False

    @staticmethod
    def _get_num_harvesters(creep):
        return len([Game.creeps[name] for name in Object.keys(Game.creeps)
                    if str(Game.creeps[name].memory.role) == Harvester.role and Game.creeps[name].room == creep.room])

    @staticmethod
    def _should_be_builder(creep):
        if Worker._get_num_harvesters(creep) >= 2:
            if len(creep.room.find(FIND_CONSTRUCTION_SITES)) > 0:
                return 'construction sites exist'
            structures_in_room = creep.room.find(FIND_STRUCTURES)
            if creep.memory.source:
                target = Worker.get_closest_to_creep(
                    creep,
                    structures_in_room.filter(
                        lambda s: s.hits < s.hitsMax / 2)
                )
                if target:
                    creep.memory.target = target.id
                    return 'structures need repair {}'.format(target.structureType)
            claimers = [Game.creeps[creep] for creep in Object.keys(Game.creeps) if Game.creeps[creep].memory.role == Claimer.role]

            for claimer in claimers:
                unbuilt_spawn = _(claimer.room.find(FIND_CONSTRUCTION_SITES).filter(
                    lambda s: s.structureType == STRUCTURE_SPAWN
                )).sample()
                if unbuilt_spawn:
                    return True

    @staticmethod
    def _should_be_harvester(creep):
        if Worker._get_num_harvesters(creep) < 1:
            return 'not enough harvesters'
        else:
            structures_in_room = creep.room.find(FIND_STRUCTURES)
            if creep.memory.source:
                target = Worker.get_closest_to_creep(
                    creep,
                    structures_in_room.filter(
                        lambda s: s.hits < s.hitsMax / 2)
                )
                if target:
                    creep.memory.target = target.id
                    return False
            claimers = [Game.creeps[creep] for creep in Object.keys(Game.creeps) if Game.creeps[creep].memory.role == Claimer.role]

            for claimer in claimers:
                unbuilt_spawn = _(claimer.room.find(FIND_CONSTRUCTION_SITES).filter(
                    lambda s: s.structureType == STRUCTURE_SPAWN
                )).sample()
                if unbuilt_spawn:
                    return False
            if len(creep.room.find(FIND_CONSTRUCTION_SITES)) <= 0:
                return 'no construction sites'

    @staticmethod
    def _become_builder(creep):
        creep.memory.role = Builder.role
        del creep.memory.target

    @staticmethod
    def _become_harvester(creep):
        creep.memory.role = Harvester.role
        del creep.memory.target

    @staticmethod
    def _get_source(creep):
        if creep.memory.source:
            source = Game.getObjectById(creep.memory.source)
            if source:
                if source.energyCapacity:
                    if source.energy <= 0:
                        del creep.memory.source
        if not source:
            containers = [Memory.creeps[creep].source_container for creep in Object.keys(Game.creeps)]
            source = Worker.get_closest_to_creep(creep, creep.room.find(FIND_STRUCTURES).filter(
                lambda s: (s.structureType == STRUCTURE_CONTAINER or s.structureType == STRUCTURE_STORAGE)
                and not containers.includes(s.id)
                and s.store[RESOURCE_ENERGY] > creep.carryCapacity * 2
            ))
            if source:
                creep.memory.source = source.id
        if not source:
            source = _(creep.room.find(FIND_DROPPED_RESOURCES).filter(
                lambda r: r.resourceType == RESOURCE_ENERGY
            )).sample()
        if source:
            creep.memory.source = source.id
        if not source:
            if creep.room.storage:
                source = creep.room.storage
                creep.memory.source = source.id
            if not source:
                source = Miner.get_closest_to_creep(
                    creep,
                    creep.room.find(FIND_STRUCTURES).filter(
                        lambda s: s.structureType == STRUCTURE_CONTAINER and s.store[RESOURCE_ENERGY] > creep.carryCapacity
                    ))
            if not source:
                # Get a random new source and save it
                source = _(creep.room.find(FIND_SOURCES).filter(
                    lambda s: s.energy > 0
                )).sample()
                if source:
                    creep.memory.source = source.id
        return source

    @staticmethod
    def _harvest_source(creep, source):
        if not source:
            del creep.memory.source
            return
        if source.structureType == STRUCTURE_CONTAINER or source.structureType == STRUCTURE_STORAGE:
            res = creep.withdraw(source, RESOURCE_ENERGY)
            if res == ERR_NOT_IN_RANGE:
                creep.moveTo(source)
            elif res == ERR_NOT_ENOUGH_ENERGY or ERR_NOT_ENOUGH_RESOURCES:
                del creep.memory.source
                Worker._get_source(creep)
        else:
            if source.resourceType == RESOURCE_ENERGY:
                res = creep.pickup(source)
                if res == ERR_NOT_IN_RANGE:
                    creep.moveTo(source)
                elif res == ERR_NOT_ENOUGH_ENERGY:
                    del creep.memory.source
                    Worker._get_source(creep)
                elif res == ERR_BUSY:
                    pass
                elif res != OK:
                    console.log('{} cannot withdraw from {} {}'.format(creep.memory.role, source.structureType, res))
                return res

            # If we're near the source, harvest it - otherwise, move to it.
            else:
                result = creep.harvest(source)
                if result == ERR_NOT_IN_RANGE:
                    creep.moveTo(source)
                elif result == ERR_NOT_ENOUGH_ENERGY:
                    return
                elif result != OK:
                    console.log("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, source, result))
                    del creep.memory.source
                return result

    @staticmethod
    def _transfer_energy(creep, target):
        if Worker._is_close_to_target(creep, target):
            # If we are targeting a spawn or extension, transfer energy. Otherwise, use upgradeController on it.
            if target.energyCapacity:
                Worker._transfer_energy_to_target(creep, target)
            else:
                Worker._upgrade_controller(creep, target)
        else:
            creep.moveTo(target)

    @staticmethod
    def _upgrade_controller(creep, target):
        creep.upgradeController(target)
        if not creep.pos.inRangeTo(target, 2):
            creep.moveTo(target)

    @staticmethod
    def _transfer_energy_to_target(creep, target):
        result = creep.transfer(target, RESOURCE_ENERGY)
        if result == OK:
            del creep.memory.target
        elif result == ERR_NOT_IN_RANGE:
            creep.moveTo(target)
        elif result == ERR_FULL:
            del creep.memory.target
        elif result == ERR_INVALID_TARGET:
            del creep.memory.target
        else:
            console.log("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                creep.name, target, RESOURCE_ENERGY, result))
            del creep.memory.target
        return result

    @staticmethod
    def _is_close_to_target(creep, target):
        # If we are targeting a spawn or extension, we need to be directly next to it - otherwise, we can be 3 away.
        if target.energyCapacity:
            return creep.pos.isNearTo(target)
        else:
            return creep.pos.inRangeTo(target, 3)

    @staticmethod
    def creep_empty(creep):
        creep.memory.filling = True
        del creep.memory.target

    @staticmethod
    def creep_full(creep):
        creep.memory.filling = False
        del creep.memory.source

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
            Harvester.run_creep(creep)
            return

        Worker._pre_run_checks(creep)

        if creep.memory.filling:
            Builder._harvest_source(creep, Builder._get_source(creep))

        else:
            target = Builder._get_target(creep)
            if target:
                if not target:
                    del creep.memory.target
                    return
                if target.structureType == STRUCTURE_ROAD or target.structureType == STRUCTURE_CONTAINER:
                    if target.hits >= target.hitsMax / 3 * 2:
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
                    structures_in_room.filter(lambda s: s.hits < s.hitsMax / 2)
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
            claimers = [Game.creeps[creep] for creep in Object.keys(Game.creeps) if Game.creeps[creep].memory.role == Claimer.role]
            for claimer in claimers:
                unbuilt_spawn = _(claimer.room.find(FIND_CONSTRUCTION_SITES).filter(
                    lambda s: s.structureType == STRUCTURE_SPAWN
                )).sample()
                if unbuilt_spawn:
                    creep.memory.target = unbuilt_spawn.id
                    return unbuilt_spawn
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
            Harvester._harvest_source(creep, Harvester._get_source(creep))
        else:
            Harvester._transfer_energy(creep, Harvester._get_target(creep))

    @staticmethod
    def _get_target(creep):
        # If we have a saved target, use it
        if creep.memory.target:
            target = Game.getObjectById(creep.memory.target)
        else:
            structures_in_room = creep.room.find(FIND_STRUCTURES)
            # fill extentions and spawns first
            if len([creep for creep in Object.keys(Game.creeps) if Game.creeps[creep].memory.role == Carrier.role]) <= 0:
                target = Worker.get_closest_to_creep(
                    creep,
                    structures_in_room.filter(
                        lambda s: (s.structureType == STRUCTURE_EXTENSION or s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_TOWER)
                                  and s.energy < s.energyCapacity
                ))
            if not target:
                # Get a random new target.
                target = _(structures_in_room).filter(lambda s: s.structureType == STRUCTURE_CONTROLLER).sample()
            if target:
                creep.memory.target = target.id
        return target


class Miner(Harvester):
    role = 'miner'

    body_composition = {
        'small': [WORK, WORK, MOVE],
        'medium': [WORK, WORK, WORK, MOVE],
        'large': [WORK, WORK, WORK, WORK, MOVE],
        'xlarge': [WORK, WORK, WORK, WORK, WORK, MOVE]
    }

    @staticmethod
    def factory(spawn, num_workers):
        body = None
        i = 0
        num_workers = 5
        while True:
            size = Worker.num_creep_to_size[num_workers - i]
            if not size:
                return
            if spawn.room.energyAvailable >= Miner._calculate_creation_cost(Miner.body_composition[size]):
                body = Miner.body_composition[size]
                break
            i += 1
        if body:
            console.log('spawning new {} worker creep'.format(size))
            Creeps.create(body, spawn, Miner.role)

    @staticmethod
    def run_creep(creep):
        """
        Runs a creep as a generic harvester.
        :param creep: The creep to run
        """
        source = Miner._get_source(creep)
        if not creep.memory.on_source_container:
            creep.moveTo(Game.getObjectById(creep.memory.source_container))
        if len(creep.pos.lookFor(STRUCTURE_CONTAINER)) > 0:
            creep.memory.on_source_container = True
        else:
            creep.harvest(source)
            creep.drop(RESOURCE_ENERGY)

        #if Miner._is_creep_full(creep):
        #    Miner.creep_full(creep)
        #elif Miner._is_creep_empty(creep):
        #    Miner.creep_empty(creep)
        #if creep.memory.filling:
        #else:
        #    Miner._transfer_energy(creep, Miner._get_target(creep))

    @staticmethod
    def _get_target(creep):
        if creep.memory.target:
            target = Game.getObjectById(creep.memory.target)
        else:
            target = Miner.get_closest_to_creep(
                creep,
                creep.room.find(FIND_STRUCTURES).filter(
                    lambda s: s.structureType == STRUCTURE_CONTAINER
                ))
            if target:
                creep.memory.target = target.id
        return target

    @staticmethod
    def _get_source(creep):
        source = creep.memory.source
        if source:
            s = Game.getObjectById(source)
            if not s.structureType == STRUCTURE_CONTAINER:
                return s

        worked_sources = [Memory.creeps[creep].source for creep in Object.keys(Game.creeps) if Memory.creeps[creep].role == 'miner']
        sources = creep.room.find(FIND_SOURCES).filter(
            lambda s: not worked_sources.includes(s.id)
        )
        if len(sources) > 0:
            source = sources[0]
            containers = source.pos.findInRange(FIND_STRUCTURES, 2).filter(
                lambda s: s.structureType == STRUCTURE_CONTAINER
            )
            if len(containers) > 0:
                source_container = containers[0]
            creep.memory.source = source.id
            creep.memory.source_container = source_container.id
            return source

    @staticmethod
    def _transfer_energy(creep, target):
        res = creep.transfer(target, RESOURCE_ENERGY)
        if res == ERR_NOT_IN_RANGE:
            creep.moveTo(target)
        elif res == ERR_FULL:
            pass
        elif res != OK and res != ERR_INVALID_TARGET:
            console.log('{} cant transfer to {} {}'.format(Miner.role, target, res))

    @staticmethod
    def creep_empty(creep):
        creep.memory.filling = True
        del creep.memory.target

    @staticmethod
    def creep_full(creep):
        creep.memory.filling = False


class Carrier(Worker):
    role = 'carrier'
    body_composition = {
        'small': [CARRY, CARRY,
                  MOVE, MOVE],
        'medium': [CARRY, CARRY, CARRY, CARRY,
                   MOVE, MOVE, MOVE, MOVE],
        'large': [CARRY, CARRY, CARRY, CARRY, CARRY,
                  CARRY, CARRY, CARRY, CARRY, CARRY,
                  CARRY, CARRY, CARRY,
                  MOVE, MOVE, MOVE, MOVE, MOVE,
                  MOVE, MOVE, MOVE],
        'xlarge': [CARRY, CARRY, CARRY, CARRY, CARRY,
                   CARRY, CARRY, CARRY, CARRY, CARRY,
                   CARRY, CARRY, CARRY, CARRY, CARRY,
                   CARRY, CARRY, CARRY, CARRY, CARRY,
                   MOVE, MOVE, MOVE, MOVE, MOVE,
                   MOVE, MOVE, MOVE, MOVE, MOVE]
    }

    @staticmethod
    def factory(spawn, num_workers):
        body = None
        i = 0
        if num_workers > 4:
            num_workers = 4
        while True:
            size = Carrier.num_creep_to_size[num_workers - i]
            if not size:
                return
            if spawn.room.energyAvailable >= Carrier._calculate_creation_cost(Carrier.body_composition[size]):
                body = Carrier.body_composition[size]
                break
            i += 1

        console.log('spawning new {} worker creep'.format(size))
        Creeps.create(body, spawn, Carrier.role)

    @staticmethod
    def run_creep(creep):
        if _.sum(creep.carry) <= 0:
            creep.memory.filling = True
        else:
            creep.memory.filling = False
            del creep.memory.source
        if creep.memory.source:
            source = Game.getObjectById(creep.memory.source)
            if source and source.structureType == STRUCTURE_STORAGE:
                del creep.memory.source
        else:
            miner_containers = [Game.getObjectById(Memory.creeps[miner].source_container) for miner in Object.keys(Game.creeps) if Memory.creeps[miner].role == 'miner' and Game.creeps[miner].room == creep.room]
            miner_containers = [container for container in miner_containers if container and container.store[RESOURCE_ENERGY] > creep.carryCapacity * 2]
            if not source:
                source = _(creep.room.find(FIND_DROPPED_RESOURCES).filter(
                    lambda r: r.resourceType == RESOURCE_ENERGY and r.amount >= creep.carryCapacity
                )).sample()
            if source:
                creep.memory.source = source.id
            if miner_containers:
                source = reversed(sorted(miner_containers, lambda c: c.store[RESOURCE_ENERGY]))[0]
                if source:
                    creep.memory.source = source.id
            if not source:
                source = creep.room.storage
                if source:
                    creep.memory.source = source.id
        if creep.memory.filling:
            res = Carrier._harvest_source(creep, source)
        else:
            res = Carrier._transfer_energy_to_target(creep, Carrier._get_target(creep))
            if res == ERR_FULL or res == ERR_INVALID_TARGET:
                del creep.memory.target

    @staticmethod
    def _get_target(creep):
        if creep.memory.target:
            return Game.getObjectById(creep.memory.target)
        structures_in_room = creep.room.find(FIND_STRUCTURES)
        target = Worker.get_closest_to_creep(
            creep,
            structures_in_room.filter(
                lambda s: (s.structureType == STRUCTURE_EXTENSION or s.structureType == STRUCTURE_SPAWN or s.structureType == STRUCTURE_TOWER)
                          and s.energy < s.energyCapacity
            ))
        if target:
            creep.memory.target = target.id
            return target
        containers = [Memory.creeps[creep].source_container for creep in Object.keys(Game.creeps)]
        unmined_containers = structures_in_room.filter(
            lambda s: (s.structureType == STRUCTURE_CONTAINER or s.structureType == STRUCTURE_STORAGE)
                      and not containers.includes(s.id) and s.store[RESOURCE_ENERGY] < s.storeCapacity*0.7
        )
        if unmined_containers:
            target = sorted(unmined_containers, lambda c: c.storeCapacity / c.store[RESOURCE_ENERGY] and c.store[RESOURCE_ENERGY] < c.storeCapacity *0.9)[0]
            if target:
                creep.memory.target = target.id
                return target
        target = Game.creeps[creep.name].room.storage
        if target:
            creep.memory.target = target.id
            return target


class Claimer(Worker):
    role = 'claimer'

    body_composition = {
        'small': [CLAIM, MOVE, MOVE, MOVE]
    }

    @staticmethod
    def factory(spawn, num_workers):
        body = None
        i = 0
        while True:
            size = 'small'
            if spawn.room.energyAvailable >= Claimer._calculate_creation_cost(Claimer.body_composition[size]):
                body = Claimer.body_composition[size]
                break
            i += 1

        console.log('spawning new {} worker creep'.format(size))
        Creeps.create(body, spawn, Claimer.role)

    @staticmethod
    def run_creep(creep):
        for flag in Object.keys(Game.flags):
            if not Game.flags[flag].room:
                creep.moveTo(Game.flags[flag].pos)
            else:
                if Game.flags[flag].room.controller:
                    if creep.memory.target:
                        controller = Game.getObjectById(creep.memory.target)
                    else:
                        controller = Game.flags[flag].room.controller
                        creep.memory.target = controller.id

                    if creep.claimController(controller) != OK:
                        creep.moveTo(controller)
                        creep.claimController(controller)

