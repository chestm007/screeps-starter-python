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

class RemoteMiner(Worker):
    role = 'remote_miner'

    body_composition = [
        [WORK, WORK, CARRY, MOVE],
        [WORK, WORK, WORK, CARRY, MOVE],
        [WORK, WORK, WORK, CARRY, MOVE],
        [WORK, WORK, WORK, WORK, WORK,
         MOVE, MOVE, MOVE, MOVE, MOVE],
    ]

    def run_creep(self):
        """
        Runs a creep as a generic harvester.
        :param creep: The creep to run
        """
        if self.creep.room.name != self.creep.memory.room:
            # if not find a route to there
            exit_dir = self.creep.room.findExitTo(self.creep.memory.room)
            if exit_dir:
                room_exit = self.creep.pos.findClosestByRange(exit_dir)
                if room_exit:
                    self.creep.moveTo(room_exit)
        else:
            source = self._get_source()
            if self.creep.memory.source_container:
                if not self.creep.memory.on_source_container:
                    self.creep.moveTo(Game.getObjectById(self.creep.memory.source_container))
            if len(self.creep.pos.lookFor(STRUCTURE_CONTAINER)) > 0:
                self.creep.memory.on_source_container = True
            self.creep.moveTo(source)
            self.creep.harvest(source)

    def _get_source(self):
        source_container = None
        source = None
        src = self.creep.memory.source
        if self.creep.memory.room == self.creep.room:
            if src:
                s = Game.getObjectById(src)
                if not s.structureType == STRUCTURE_CONTAINER:
                    source = s
                if not self.creep.memory.source_container:
                    containers = source.pos.findInRange(FIND_STRUCTURES, 2).filter(
                        lambda struct: struct.structureType == STRUCTURE_CONTAINER
                    )
                    if len(containers) > 0:
                        source_container = containers[0]
                        self.creep.memory.source_container = source_container.id
        if source:
            return source