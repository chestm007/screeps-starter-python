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
                    WORK, WORK,
                   CARRY, CARRY,
                   MOVE, MOVE, MOVE, MOVE]
    }

    @staticmethod
    def factory(spawn, num_workers, extra_memory_args=None):
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
        return Creeps.create(body, spawn, Worker.role)

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


class Builder(Worker):
    role = 'builder'

    def run_creep(self):
        if self._should_be_harvester():
            self._become_harvester()
            Harvester.run_creep(self)
            return

        self._pre_run_checks()

        if self.creep.memory.filling:
            self._harvest_source(self._get_source())

        else:
            target = self._get_target()
            if target:
                if not target:
                    del self.creep.memory.target
                    return
                if target.structureType == STRUCTURE_ROAD or target.structureType == STRUCTURE_CONTAINER:
                    if target.hits >= target.hitsMax / 3 * 2:
                        del self.creep.memory.target
                        self._get_target()
                    res = self.creep.repair(target)
                    if res == ERR_NOT_IN_RANGE:
                        self.creep.moveTo(target)
                        return
                    elif res == OK:
                        return
                res = self.creep.build(target)
                if res == ERR_NOT_IN_RANGE:
                    self.creep.moveTo(target)
                    return
                elif res == OK:
                    return
            del self.creep.memory.target

    def _get_target(self):
        target = None
        if self.creep.memory.target:
            target = Game.getObjectById(self.creep.memory.target)
        else:
            if self.creep.memory.source:
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
            claimers = [Game.creeps[creep] for creep in Object.keys(Game.creeps)
                        if Game.creeps[creep].memory.role == Claimer.role]
            for claimer in claimers:
                unbuilt_spawn = _(claimer.room.find(FIND_CONSTRUCTION_SITES).filter(
                    lambda s: s.structureType == STRUCTURE_SPAWN
                )).sample()
                if unbuilt_spawn:
                    self.creep.memory.target = unbuilt_spawn.id
                    return unbuilt_spawn
        return target


class Harvester(Worker):
    role = 'harvester'

    def run_creep(self):
        """
        Runs a creep as a generic harvester.
        """
        if self._should_be_builder():
            self._become_builder()
            Builder.run_creep(self)
            return

        self._pre_run_checks()

        if self.creep.memory.filling:
            self._harvest_source(self._get_source())
        else:
            self._transfer_energy(self._get_target())

    def _get_target(self):
        target = None
        # If we have a saved target, use it
        if self.creep.memory.target:
            target = Game.getObjectById(self.creep.memory.target)
        else:
            # fill extentions and spawns first
            if len([creep for creep in Object.keys(Game.creeps)
                    if Game.creeps[creep].memory.role == Carrier.role]) <= 0:
                target = self.get_closest_to_creep(
                    self.structures_in_room.filter(
                        lambda s: (
                                      s.structureType == STRUCTURE_EXTENSION
                                      or s.structureType == STRUCTURE_SPAWN
                                      or s.structureType == STRUCTURE_TOWER
                                  ) and s.energy < s.energyCapacity
                    ))
            if not target:
                # Get a random new target.
                target = _(self.structures_in_room).filter(
                    lambda s: s.structureType == STRUCTURE_CONTROLLER
                ).sample()
            if target:
                self.creep.memory.target = target.id
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
    def factory(spawn, num_workers, extra_memory_args=None):
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
            return Creeps.create(body, spawn, Miner.role)

    def run_creep(self):
        """
        Runs a creep as a generic harvester.
        :param creep: The creep to run
        """
        source = self._get_source()
        if self.creep.memory.source_container:
            if not self.creep.memory.on_source_container:
                self.creep.moveTo(Game.getObjectById(self.creep.memory.source_container))
            if len(self.creep.pos.lookFor(STRUCTURE_CONTAINER)) > 0:
                self.creep.memory.on_source_container = True
        else:
            self.creep.moveTo(source)
        self.creep.harvest(source)
        self.creep.drop(RESOURCE_ENERGY)

    def _get_target(self):
        if self.creep.memory.target:
            target = Game.getObjectById(self.creep.memory.target)
        else:
            target = self.get_closest_to_creep(
                self.structures_in_room.filter(
                    lambda s: s.structureType == STRUCTURE_CONTAINER
                ))
            if target:
                self.creep.memory.target = target.id
        return target

    def _get_source(self):
        source_container = None
        source = self.creep.memory.source
        if source:
            s = Game.getObjectById(source)
            if not s.structureType == STRUCTURE_CONTAINER:
                return s

        worked_sources = [Memory.creeps[creep].source for creep in Object.keys(Game.creeps)
                          if Memory.creeps[creep].role == 'miner']
        sources = self.resources_in_room.filter(
            lambda src: not worked_sources.includes(src.id)
        )
        if len(sources) > 0:
            source = sources[0]
            containers = source.pos.findInRange(FIND_STRUCTURES, 2).filter(
                lambda struct: struct.structureType == STRUCTURE_CONTAINER
            )
            if len(containers) > 0:
                source_container = containers[0]
            self.creep.memory.source = source.id
            self.creep.memory.source_container = source_container.id
            return source

    def _transfer_energy(self, target):
        res = self.creep.transfer(target, RESOURCE_ENERGY)
        if res == ERR_NOT_IN_RANGE:
            self.creep.moveTo(target)
        elif res == ERR_FULL:
            pass
        elif res != OK and res != ERR_INVALID_TARGET:
            console.log('{} cant transfer to {} {}'.format(self.role, target, res))

    def creep_empty(self):
        self.creep.memory.filling = True
        del self.creep.memory.target

    def creep_full(self):
        self.creep.memory.filling = False


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
    def factory(spawn, num_workers, extra_memory_args=None):
        i = 0
        if num_workers > 4:
            num_workers = 4
        min_size = spawn.room.controller.level
        if min_size > 4:
            min_size = 4
        if num_workers < 1:
            min_size = 0
        else:
            num_workers = 4
        while True:
            size = Carrier.num_creep_to_size[num_workers - i]
            if not size:
                return
            if spawn.room.energyAvailable >= Carrier._calculate_creation_cost(Carrier.body_composition[size]):
                body = Carrier.body_composition[size]
                break
            i += 1
            if num_workers - i < min_size:
                break

        console.log('spawning new {} worker creep'.format(size))
        return Creeps.create(body, spawn, Carrier.role)

    def run_creep(self):
        source = None
        if _.sum(self.creep.carry) <= 0:
            self.creep.memory.filling = True
        else:
            self.creep.memory.filling = False
            del self.creep.memory.source
        if self.creep.memory.source:
            source = Game.getObjectById(self.creep.memory.source)
            if source and source.structureType == STRUCTURE_STORAGE:
                del self.creep.memory.source
        else:
            miner_containers = [
                Game.getObjectById(Memory.creeps[miner].source_container)
                for miner in Object.keys(Game.creeps)
                if Memory.creeps[miner].role == 'miner' and Game.creeps[miner].room == self.creep.room]

            miner_containers = [
                container for container in miner_containers
                if container
                and container.store[RESOURCE_ENERGY] > self.creep.carryCapacity * 2]

            if not source:
                source = _(self.dropped_resources_in_room.filter(
                    lambda r: r.resourceType == RESOURCE_ENERGY and r.amount >= self.creep.carryCapacity
                )).sample()
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
            res = self._transfer_energy_to_target(self._get_target())
            if res == ERR_FULL or res == ERR_INVALID_TARGET:
                del self.creep.memory.target

    def _get_target(self):
        if self.creep.memory.target:
            return Game.getObjectById(self.creep.memory.target)

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


class Claimer(Worker):
    role = 'claimer'

    body_composition = [
        [CLAIM, CLAIM, MOVE, MOVE]
    ]

    @staticmethod
    def factory(spawn, num_workers, room, target):
        size = 'small'
        if spawn.room.energyAvailable >= Claimer._calculate_creation_cost(Claimer.body_composition[size]):
            body = Claimer.body_composition[size]

        console.log('spawning new {} worker creep'.format(size))
        name = spawn.room.name + Game.time
        creep = spawn.spawnCreep(body, name)
        Memory.creeps[name] = {'role': Claimer.role, 'room': room, 'target': target}
        return creep
        return Creeps.create(body, spawn, Claimer.role, extra_memory_args=extra_memory_args)

    def run_creep(self):
        return
        target = self._get_target()
        if self.creep.memory.flag:
            if self.creep.memory.flag.startswith('claim'):
                res = self.creep.claimController(target)
            elif self.creep.memory.flag.startswith('reserve'):
                res = self.creep.reserveController(target)
            else:
                return
            if res != OK:
                self.creep.moveTo(target)

    def _get_target(self):
        target = Game.getObjectById(self.creep.memory.target)
        if target:
            if target.room != self.creep.room:
                target = None
        if not target:
            if self.creep.memory.flag:
                flag = Game.flags[self.creep.memory.flag.replace('Spawn', '')]
            if not flag:
                worked_flags = [Memory.creeps[creep].flag for creep in Object.keys(Game.creeps)
                                if Memory.creeps[creep].role == 'claimer']

                flags = Object.keys(Game.flags).filter(
                    lambda f: not worked_flags.includes(f)
                    and (str(f).startswith('claim') or str(f).startswith('reserve'))
                    and not str(f).endswith('Spawn')
                )
                if len(flags) > 0:
                    flag = Game.flags[flags[0]]
                    self.creep.memory.flag = flag.name
            if flag:
                if flag.room == self.creep.room:
                    target = Game.flags[flag.name].room.controller
                    if target:
                        self.creep.memory.target = target.id
        if target:
            return target
        if flag:
            return flag


class RemoteMiner(Worker):
    role = 'remote_miner'

    body_composition = {
        'small': [WORK, WORK, CARRY, MOVE],
        'medium': [WORK, WORK, WORK, CARRY, MOVE],
        'large': [WORK, WORK, WORK, CARRY, MOVE],
        'xlarge': [WORK, WORK, WORK, WORK, WORK,
                   MOVE, MOVE, MOVE, MOVE, MOVE],
    }

    @staticmethod
    def factory(spawn, num_workers, extra_memory_args=None):
        _class = RemoteMiner
        size = 'xlarge'
        if spawn.room.energyAvailable >= _class._calculate_creation_cost(_class.body_composition[size]):
            body = _class.body_composition[size]

            console.log('spawning new {} {} creep'.format(size, _class.__name__))
            return Creeps.create(body, spawn, _class.role, extra_memory_args)

    def run_creep(self):
        """
        Runs a creep as a generic harvester.
        :param creep: The creep to run
        """
        source = self._get_source()
        if self.creep.memory.source_container:
            if not self.creep.memory.on_source_container:
                self.creep.moveTo(Game.getObjectById(self.creep.memory.source_container))
        else:
            if self.creep.memory.flag:
                self.creep.moveTo(Game.flags[self.creep.memory.flag])
                container_site = self.creep.pos.findInRange(FIND_CONSTRUCTION_SITES, 1).filter(
                    lambda s: s.structureType == STRUCTURE_CONTAINER
                )
                if container_site:
                    res = self.creep.build(container_site)
        if len(self.creep.pos.lookFor(STRUCTURE_CONTAINER)) > 0:
            self.creep.memory.on_source_container = True
        self.creep.harvest(source)

    def _get_source(self):
        source_container = None
        source = self.creep.memory.source
        if self.creep.memory.flag:
            flag = Game.flags[self.creep.memory.flag]
        if not flag:
            worked_flags = [Memory.creeps[creep].flag for creep in Object.keys(Game.creeps)
                            if Memory.creeps[creep].role == 'remote_miner']

            flags = Object.keys(Game.flags).filter(
                lambda f: not worked_flags.includes(f)
                and str(f).startswith('RemoteMine')
                and not str(f).startswith('claim')
                and not str(f).startswith('reserve')
                and not str(f).endswith('Storage')
                and not str(f).endswith('Spawn')
            )
            if len(flags) > 0:
                flag = Game.flags[flags[0]]
                self.creep.memory.flag = flag.name
        if flag:
            if flag.room == self.creep.room:
                if source:
                    s = Game.getObjectById(source)
                    if not s.structureType == STRUCTURE_CONTAINER:
                        return s
                sources = flag.pos.findInRange(FIND_SOURCES, 1)
                if sources:
                    source = sources[0]
                    if source:
                        self.creep.memory.source = source.id
                        containers = source.pos.findInRange(FIND_STRUCTURES, 2).filter(
                            lambda struct: struct.structureType == STRUCTURE_CONTAINER
                        )
                        if len(containers) > 0:
                            source_container = containers[0]
                            self.creep.memory.source_container = source_container.id
        if source:
            return source


class RemoteCarrier(Worker):
    role = 'remote_carrier'
    body_composition = {
        'large': [CARRY, CARRY, CARRY, CARRY, CARRY,
                  CARRY, CARRY, CARRY, CARRY, CARRY,
                  CARRY, CARRY, CARRY, CARRY, CARRY,
                  CARRY, CARRY, CARRY,
                  MOVE, MOVE, MOVE, MOVE, MOVE,
                  MOVE, MOVE, MOVE, MOVE],
    }

    @staticmethod
    def factory(spawn, num_workers, extra_memory_args=None):
        _class = RemoteCarrier
        size = 'large'
        if spawn.room.energyAvailable >= _class._calculate_creation_cost(_class.body_composition[size]):
            body = _class.body_composition[size]

            console.log('spawning new {} {} creep'.format(size, _class.__name__))
            return Creeps.create(body, spawn, _class.role, extra_memory_args)

    def run_creep(self):
        #on_road = _(self.creep.pos.lookFor(LOOK_STRUCTURES)).filter(
        #    lambda s: s.structureType == STRUCTURE_ROAD
        #).sample()
        #if not on_road:
        #    self.creep.pos.createConstructionSite(STRUCTURE_ROAD)
        if _.sum(self.creep.carry) < self.creep.carryCapacity:
            source = self._get_source()
            if source:
                dropped_energy = source.pos.lookFor(RESOURCE_ENERGY)
                if len(dropped_energy) > 0:
                    self.creep.pickup(dropped_energy[0])
                source.transfer(self.creep, RESOURCE_ENERGY)
                self.creep.moveTo(source)
        else:
            target = self._get_target()
            if target:
                self.creep.transfer(target, RESOURCE_ENERGY)
                self.creep.moveTo(target)
            else:
                flag = Game.getObjectById(self.creep.memory.flag)
                if not flag:
                    move_to_flag = Game.creeps[self.creep.memory.source]
                    if move_to_flag:
                        flag = Game.flags[move_to_flag.memory.flag + 'Storage']
                        if flag:
                            self.creep.memory.flag = flag.name
                else:
                    del self.creep.memory.source
                self.creep.moveTo(flag)

    def _get_source(self):
        source = None
        if self.creep.memory.source:
            source = Game.creeps[self.creep.memory.source]
            if source:
                return source
            del self.creep.memory.source
        carried_sources = [Memory.creeps[creep].source for creep in Object.keys(Game.creeps)
                           if Memory.creeps[creep].role == 'remote_carrier']
        sources = Object.keys(Game.creeps).filter(
            lambda creep: not carried_sources.includes(creep)
            and Game.creeps[creep].memory.role == 'remote_miner'
        )
        if len(sources) > 0:
            source = Game.creeps[sources[0]]
        if source:
            self.creep.memory.source = source.name
            return source
        else:
            del self.creep.memory.source

    def _get_target(self):
        if self.creep.room.storage:
            target = self.creep.room.storage
        elif self.creep.memory.target:
            target = Game.getObjectById(self.creep.memory.target)
            if target:
                self.creep.memory.target = target.id
        else:
            return
        return target


class RemoteBuilder(Worker):
    role = 'remote_builder'

    body_composition = {
        'large': [WORK,
                  CARRY, CARRY, CARRY, CARRY,
                  MOVE, MOVE, MOVE, MOVE],
    }

    @staticmethod
    def factory(spawn, num_workers, extra_memory_args=None):
        _class = RemoteBuilder
        size = 'large'
        if spawn.room.energyAvailable >= _class._calculate_creation_cost(_class.body_composition[size]):
            body = _class.body_composition[size]

            console.log('spawning new {} {} creep'.format(size, _class.__name__))
            return Creeps.create(body, spawn, _class.role, extra_memory_args)

    def run_creep(self):
        if self.creep.carry[RESOURCE_ENERGY] >= self.creep.carryCapacity:
            self.creep.memory.filling = False
        elif self.creep.carry[RESOURCE_ENERGY] <= 0:
            self.creep.memory.filling = True
        if self.creep.memory.filling:
            source = self._get_source()
            if source:
                self.creep.moveTo(source)
                self.creep.withdraw(source, RESOURCE_ENERGY)
                self.creep.harvest(source)
        else:
            target = self._get_target()
            if target:
                if target.color:
                    self.creep.moveTo(target)
                res = self.creep.build(target)
                if res == ERR_INVALID_TARGET:
                    res = self.creep.repair(target)
                if res == ERR_NOT_IN_RANGE:
                    self.creep.moveTo(target)
                    self.creep.build(target)
                if target.hits:
                    if target.hits >= target.hitsMax:
                        del self.creep.memory.target

    def _get_source(self):
        source = Game.getObjectById(self.creep.memory.source)
        if not source:
            for spawn in Object.keys(Game.spawns):
                cur_spawn = Game.spawns[spawn]
                if cur_spawn:
                    if cur_spawn.room == self.creep.room:
                        source = cur_spawn.room.storage
                        if source:
                            self.creep.memory.source = source.id
        target = Game.getObjectById(self.creep.memory.target)
        if target and target.structureType == STRUCTURE_SPAWN:
            if not source or not source.structureType == RESOURCE_ENERGY:
                source = self.creep.pos.findClosestByRange(FIND_SOURCES)
                console.log(source)
                if source:
                    self.creep.memory.source = source.id
        return source

    def _get_target(self):
        target = Game.getObjectById(self.creep.memory.target)
        if not target:
            if self.creep.memory.flag:
                flag = Game.flags[self.creep.memory.flag.replace('Spawn', '')]
            if not flag:
                worked_flags = [Memory.creeps[creep].flag for creep in Object.keys(Game.creeps)
                                if Memory.creeps[creep].role == 'remote_builder']

                flags = Object.keys(Game.flags).filter(
                    lambda f: not worked_flags.includes(f)
                              and (
                                  str(f).startswith('reserve')
                                  or str(f).startswith('claim')
                              )
                )
                if len(flags) > 0:
                    flag = Game.flags[flags[0]]
                    self.creep.memory.flag = flag.name
            if flag:
                if flag.room == self.creep.room:
                    construction_sites = self.creep.room.find(FIND_CONSTRUCTION_SITES)
                    if construction_sites:
                        target = self.get_closest_to_creep(
                            construction_sites.filter(
                                lambda s: s.structureType == STRUCTURE_SPAWN
                                or s.structureType == STRUCTURE_ROAD
                            )
                        )
                    structures_in_room = self.creep.room.find(FIND_STRUCTURES)
                    if structures_in_room:
                        damaged_road = self.get_closest_to_creep(structures_in_room.filter(
                            lambda s: s.structureType == STRUCTURE_ROAD
                            and s.hits < s.hitsMax * 0.9
                        ))
                        if damaged_road:
                            target = damaged_road
        if target:
            self.creep.memory.target = target.id
            return target
        elif flag:
            return flag


