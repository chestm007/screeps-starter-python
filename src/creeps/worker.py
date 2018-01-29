from creeps.creeps import _Creep
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


class Worker(_Creep):
    role = 'harvester'

    body_composition = {
        'small': [WORK, CARRY, MOVE, MOVE],
        'medium': [WORK, WORK, CARRY, MOVE, MOVE, MOVE],
        'large': [WORK, WORK, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE],
        'xlarge': [WORK, WORK, WORK, WORK, CARRY, CARRY, CARRY, MOVE, MOVE, MOVE, MOVE, MOVE]
    }

    def _is_creep_empty(self):
        # If we're empty, start filling again and remove the saved target
        if not self.memory.filling and self.carry.energy <= 0:
            return True

    def _is_creep_full(self):
        # If we're full, stop filling up and remove the saved source
        if self.memory.filling and _.sum(self.carry) >= self.carryCapacity:
            return True

    def creep_full(self):
        self.memory.filling = False

    def creep_empty(self):
        self.memory.filling = True
        del self.memory.target

    def run_creep(self):
        if self._is_creep_empty():
            self.creep_empty()
        elif self._is_creep_full():
            self.creep_full()
        if not self.memory.filling:
            self.memory.filling = False

    def factory(self, spawn, num_workers):
        body = None
        i = 0
        while True:
            if num_workers >= len(Worker.num_creep_to_size):
                num_workers = len(Worker.num_creep_to_size) - 1
            size = Worker.num_creep_to_size[num_workers - i]
            if spawn.room.energyAvailable >= self._calculate_creation_cost(self.body_composition[size]):
                body = Worker.body_composition[size]
                break
            i += 1

        console.log('spawning new {} worker creep'.format(size))
        self.create(body, spawn, Worker.role)


class Builder(Worker):
    role = 'builder'

    def run_creep(self):
        super().run_creep()
        self.job.run(self.creep)

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

        _pre_run_checks(creep)

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


class Miner(Harvester):
    role = 'miner'

    body_composition = {
        'small': [WORK, WORK, WORK, WORK, WORK, WORK, CARRY, MOVE],
        'medium': [WORK, WORK, WORK, WORK, WORK, WORK, CARRY, MOVE],
        'large': [WORK, WORK, WORK, WORK, WORK, WORK, WORK, CARRY, MOVE],
        'xlarge': [WORK, WORK, WORK, WORK, WORK, WORK, WORK, CARRY, MOVE]
    }

    @staticmethod
    def factory(spawn, num_workers):
        body = None
        i = 0
        while True:
            size = Miner.num_creep_to_size[num_workers - i]
            if not size:
                return
            if spawn.room.energyAvailable >= Miner._calculate_creation_cost(Miner.body_composition[size]):
                body = Miner.body_composition[size]
                break
            i += 1

        console.log('spawning new {} worker creep'.format(size))
        Creeps.create(body, spawn, Miner.role)

    @staticmethod
    def run_creep(creep):
        """
        Runs a creep as a generic harvester.
        :param creep: The creep to run
        """
        if _is_creep_full(creep):
            creep_full(creep)
        elif _is_creep_empty(creep):
            creep_empty(creep)
        if creep.memory.filling:
            Miner._harvest_source(creep, Miner._get_source(creep))
        else:
            Miner._transfer_energy(creep, Miner._get_target(creep))

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

        sources = creep.room.find(FIND_SOURCES)
        sources_w_space = []
        for s in sources:
            if not Memory.rooms:
                return
            this_source = Memory.rooms[creep.room.name].resources[s.id]
            for c in Object.keys(Memory.rooms[creep.room.name].resources[s.id]['miners']):
                if this_source['miners'][c] == creep.name:
                    return s
            miners_on_source = len(this_source.miners)
            if miners_on_source >= this_source.harvest_spots:
                pass
            else:
                sources_w_space.append(s)
        source = Worker.get_closest_to_creep(creep, sources_w_space)
        if source:
            if not Memory.rooms[creep.room.name]['resources'][source.id]['miners']:
                Memory.rooms[creep.room.name]['resources'][Source.id]['miners'] = []
            Memory.rooms[creep.room.name].resources[source.id]['miners'].push(creep.name)
            creep.memory.source = source.id
            return source

    @staticmethod
    def _transfer_energy(creep, target):
        res = creep.transfer(target, RESOURCE_ENERGY)
        if res == ERR_NOT_IN_RANGE:
            creep.moveTo(target)
        elif res == ERR_FULL:
            pass
        elif res != OK:
            console.log('{} cant transfer to {} {}'.format(Miner.role, target, res))
