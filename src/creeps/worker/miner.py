from creeps.worker.worker import Harvester
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class Miner(Harvester):
    role = 'miner'

    body_composition = [
        [WORK, WORK, WORK, WORK, WORK, MOVE]
    ]

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