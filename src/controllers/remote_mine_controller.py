from Misc.globals import DEFENSIVE, NORMAL
from creeps.soldier.remote_defender import RemoteDefender
from creeps.worker.claimer import Claimer
from creeps.worker.remote_builder import RemoteBuilder
from creeps.worker.remote_carrier import RemoteCarrier
from creeps.worker.remote_miner import RemoteMiner
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')
__pragma__('noalias', 'pop')

CLAIMER = Claimer.role
REMOTE_MINER = RemoteMiner.role
REMOTE_CARRIER = RemoteCarrier.role
REMOTE_BUILDER = RemoteBuilder.role

REMOTE_DEFENDER = RemoteDefender.role

CREEP_FACTORY_MAP = {
    CLAIMER: Claimer.factory,
    REMOTE_MINER: RemoteMiner.factory,
    REMOTE_CARRIER: RemoteCarrier.factory,
    REMOTE_BUILDER: RemoteBuilder.factory,

    REMOTE_DEFENDER: RemoteDefender.factory,
}


class RemoteMineController:
    """
    responsible for spawning and coordinating remote mining of its own room
    """
    def __init__(self, hive, room_name):
        """
        :param hive: room that this remote mine is controlled be
        :param room_name: string, name of room
        """
        self._name = room_name
        self.hive = hive

        if not self.hive.memory.remote_mines[self._name]:
            self.hive.memory.remote_mines[self._name] = {}
        self.memory = self.hive.memory.remote_mines[self._name]

        self.sources = None
        if self.memory.sources:
            self.sources = [Game.getObjectById(s) for s in self.memory.sources]

        if not self.memory.controller:
            self.memory.controller = None
        self.controller = Game.getObjectById(self.memory.controller)

        if self.memory.needs_builder == undefined:
            self.memory.needs_builder = False
        self.needs_builder = self.memory.needs_builder

        self.creeps = {n: Memory.creeps[n] for n in Object.keys(Memory.creeps)
                       if Memory.creeps[n].room == self._name}
        self.claimers = {n: Memory.creeps[n] for n in Object.keys(self.creeps)
                         if Memory.creeps[n].role == CLAIMER}
        self.miners = {n: Memory.creeps[n] for n in Object.keys(self.creeps)
                       if Memory.creeps[n].role == REMOTE_MINER}
        self.carriers = {n: Memory.creeps[n] for n in Object.keys(self.creeps)
                         if Memory.creeps[n].role == REMOTE_CARRIER}
        self.defenders = {n: Memory.creeps[n] for n in Object.keys(self.creeps)
                          if Memory.creeps[n].role == REMOTE_DEFENDER}
        self.builders = {n: Memory.creeps[n] for n in Object.keys(self.creeps)
                         if Memory.creeps[n].role == REMOTE_BUILDER}

        if Game.time % 10 == 0:
            self.scan_for_hostiles()
        if Game.rooms[self._name]:
            if len(Game.rooms[self._name].find(FIND_CONSTRUCTION_SITES)) > 0:
                self.needs_builder = True
            else:
                self.needs_builder = False

        #if self.mode == DEFENSIVE:
        #    self.controller.pos.createFlag(self.hive._name + '_kite')
        #else:
        #    if self.controller:
        #        flag = self.controller.room.find(FIND_FLAGS).filter(
        #            lambda f: f.name == self.hive._name + '_kite'
        #        )
        #        if not flag:
        #            self.mode = NORMAL


    def run(self):

        # check if we have a claimer already
        if len(Object.keys(self.claimers)) <= 0:
            # if not spawn one
            # TODO: if reserve time is > 4000 ticks we should spawn a claimer
            # TODO: with only 1 CLAIM part
            self.spawn_creep(CLAIMER, {'room': self._name,
                                       'hive': self.hive._name})

        self.run_claimer()

        if not self.memory.sources or not self.memory.controller:
            if not self.memory.sources:
                self.memory.sources = None
            if not self.memory.controller:
                self.memory.controller = None

        if self.memory.sources and self.memory.controller:
            # check if there is defender
            if len(Object.keys(self.defenders)) <= 0:
                # spawn defender if there isnt one
                self.spawn_creep(REMOTE_DEFENDER, {'room': self._name,
                                                   'hive': self.hive._name})

            else:
                # get number of sources
                num_sources = len(Object.keys(self.sources))
                # get number of miners
                num_miners = len(Object.keys(self.miners))
                # spawn more miners if miners < sources
                if num_miners < num_sources:
                    miner_targets = [self.miners[c].source for c in Object.keys(self.miners)]

                    if len(miner_targets) <= 0:
                        miner_targets = []
                    unworked_sources = [s for s in self.sources
                                       if s != undefined and not miner_targets.includes(s.id)]
                    if len(unworked_sources) > 0:
                        self.spawn_creep(REMOTE_MINER, {'room': self._name,
                                                        'source': unworked_sources[0].id,
                                                        'hive': self.hive._name})

                # get number of carries
                # spawn more carries if carries < miners
                else:
                    num_carriers = len(Object.keys(self.carriers))
                    if num_carriers < num_miners:
                        carry_targets = [self.carriers[c].source for c in Object.keys(self.carriers)]
                        if len(carry_targets) <= 0:
                            carry_targets = []
                        unworked_sources = [s for s in self.sources
                                            if s != undefined and not carry_targets.includes(s.id)]
                        if len(unworked_sources) > 0:
                            self.spawn_creep(REMOTE_CARRIER, {'room': self._name,
                                                              'source': unworked_sources[0].id,
                                                              'storage': self.hive.storage.id,
                                                              'hive': self.hive._name})

                    else:
                        if self.needs_builder:
                            if len(Object.keys(self.builders)) <= 0:
                                self.spawn_creep(REMOTE_BUILDER, {'room': self._name,
                                                                  'hive': self.hive._name})

    def spawn_creep(self, creep_type, memory):
        if self.hive.all_spawned:
            spawn = self.hive.get_idle_spawn()
            if spawn:
                self.hive.create_creep(creep_type,
                                       spawn,
                                       memory)

    def scan_for_hostiles(self):
        room = Game.rooms[self._name]
        if room:
            hostiles = room.find(FIND_HOSTILE_CREEPS)
            if len(hostiles) > 0:
                self.mode = DEFENSIVE

    def run_claimer(self):
        """
        send claimer into room to reserve it and scout for sources
        :return:
        """
        for c in Object.keys(self.claimers):
            claimer = Game.creeps[c]
            if claimer:
                # check if were in the mining room
                if claimer.room.name != self._name:
                    # if not find a route to there
                    exit_dir = claimer.room.findExitTo(self._name)
                    if exit_dir:
                        room_exit = claimer.pos.findClosestByRange(exit_dir)
                        if room_exit:
                            claimer.moveTo(room_exit, {'maxRooms': 1})
                else:
                    # scout for objects if they dont exist in memory
                    if not self.memory.sources:
                        self.sources = claimer.room.find(FIND_SOURCES)
                        if self.sources:
                            self.memory.sources = [s.id for s in self.sources]
                    if not self.memory.controller:
                        self.controller = claimer.room.controller
                        if self.controller:
                            self.memory.controller = self.controller.id
                    # moveTo and reserve the room controller
                    res = claimer.reserveController(self.controller)
                    if res == ERR_NOT_IN_RANGE:
                        claimer.moveTo(self.controller, {'maxRooms': 1})
