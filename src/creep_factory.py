from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

HARVESTER = 'harvester'
SOLDIER = 'soldier'


def create_creep(creep_type, spawn):
    if creep_type == HARVESTER:
        return Harvester.factory(spawn)


class Creeps(object):
    pass

class Harvester(Creeps):
    @staticmethod
    def factory(spawn):
        (LargeHarvester if spawn.room.energyAvailable >= 350 else SmallHarvester).create(spawn)


class SmallHarvester(Harvester):
    @staticmethod
    def create(spawn):
        spawn.createCreep([WORK, CARRY, MOVE, MOVE])


class LargeHarvester(Harvester):
    @staticmethod
    def create(spawn):
        spawn.createCreep([WORK, CARRY, CARRY, MOVE, MOVE, MOVE])
