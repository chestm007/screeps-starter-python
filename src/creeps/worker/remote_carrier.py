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


class RemoteCarrier(Worker):
    role = 'remote_carrier'
    body_composition = [
        [CARRY, CARRY, CARRY, CARRY, CARRY,
         CARRY, CARRY, CARRY, CARRY, CARRY,
         CARRY, CARRY, CARRY,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE],
        [CARRY, CARRY, CARRY, CARRY, CARRY,
         CARRY, CARRY, CARRY, CARRY, CARRY,
         CARRY, CARRY, CARRY, CARRY, CARRY,
         CARRY, CARRY, CARRY,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE, MOVE, MOVE,
         MOVE, MOVE, MOVE],
    ]

    @staticmethod
    def build_body(carry_capacity):
        body = []
        [body.extend([CARRY, MOVE]) for x in range(int(carry_capacity * 1.1 / 50))]
        return body

    def run_creep(self):
        if _.sum(self.creep.carry) < self.creep.carryCapacity:
            if not self.creep.memory.empty:
                self.creep.memory.empty = True
                # we end the timer here so that we're definitely only calculating the time it took
                # to move from the miner to the storage, not including wandering around or waiting
                # for the miner to finish harvesting. if we included this time the autoscaler would
                # just keep making larger creeps FOREVER
                # self.end_travel_timer()
            if self.creep.room.name != self.creep.memory.room:
                # if not find a route to there
                exit_dir = self.creep.room.findExitTo(self.creep.memory.room)
                if exit_dir:
                    room_exit = self.creep.pos.findClosestByRange(exit_dir)
                    if room_exit:
                        self.move_by_cached_path(room_exit)
            else:
                resources = None
                res = self.creep.memory.resources
                if res:
                    resources = Game.getObjectById(res)
                if not resources:
                    src = self.creep.memory.source
                    if src:
                        source = Game.getObjectById(src)
                        if source:
                            resources = source.pos.findClosestByRange(FIND_DROPPED_RESOURCES)
                            if resources:
                                self.creep.memory.resources = resources.id
                if resources:
                    self.move_by_cached_path(resources)
                    self.creep.pickup(resources)
                else:
                    src = self.creep.memory.source
                    if src:
                        source = Game.getObjectById(src)
                        if source:
                            self.creep.moveTo(source, {'maxRooms': 1,
                                                       'range': 4})
        else:
            if self.creep.memory.empty:
                self.creep.memory.empty = False
                # self.start_travel_timer()
            if self.creep.room.name != self.creep.memory.hive:
                exit_dir = self.creep.room.findExitTo(self.creep.memory.hive)
                if exit_dir:
                    room_exit = self.creep.pos.findClosestByRange(exit_dir)
                    if room_exit:
                        self.move_by_cached_path(room_exit)
            else:
                sto = self.creep.memory.storage
                if sto:
                    storage = Game.getObjectById(sto)
                    if storage:
                        self.creep.moveTo(storage, {'maxRooms': 1})
                        self.creep.transfer(storage, RESOURCE_ENERGY)

    def start_travel_timer(self):
        self.creep.memory.depart_tick = Game.time

    def end_travel_timer(self):
        time_to_target = Game.time - self.creep.memory.depart_tick
        avg = self.hive.memory.remote_mines[self.creep.memory.room]
        if not avg:
            avg = time_to_target
        self.hive.memory.remote_mines[self.creep.memory.room].sources[self.creep.memory.source].time_to_source \
            = (time_to_target + avg) / 2

    def _get_source(self):
        pass

    def _get_target(self):
        pass
