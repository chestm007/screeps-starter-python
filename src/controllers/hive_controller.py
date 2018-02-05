from controllers.remote_mine_controller import RemoteMineController
from controllers.tower_controller import TowerController
from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class HiveController:
    def __init__(self, room_name):
        self._name = room_name
        self.room = Game.rooms[self._name]
        self.memory = self.room.memory
        self.tower_controller = TowerController(room_name)
        self.tower_controller.run_towers()
        spawns = [Game.spawns[spawn] for spawn in Object.keys(Game.spawns)]
        self.spawns = _.filter(spawns, lambda s: s.room.name == self._name)
        if self.room.storage:
            self.storage = self.room.storage
        else:
            self.storage = None

        if not self.memory.remote_mines:
            self.memory.remote_mines = {}
        self.remote_mines = [
            RemoteMineController(self, mine_name) for mine_name in Object.keys(self.memory.remote_mines)
        ]

    def run(self):
        if self.storage:
            for remote_mine in self.remote_mines:
                remote_mine.run()

    def get_idle_spawn(self):
        for spawn in self.spawns:
            if not spawn.spawning:
                return spawn