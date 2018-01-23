
from defs import *
import harvester

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
    body_composition = None

    def create(self, spawn):
        if self.body_composition is None:
            console.log('Error creating {}: no defined body composition'.format(self.__class__.__name__))
        else:
            existing_creeps = []
            for name in Object.keys(Game.creeps):
                if name.startswith(self.__class__.__name__):
                    existing_creeps.append(name)
            i = 0
            while True:
                if existing_creeps.includes('{}{}'.format(self.__class__.__name__, (len(existing_creeps) + i))):
                    i += 10
                else:
                    spawn.createCreep(self.body_composition, '{type}{number}'.format(
                        type=self.__class__.__name__,
                        number=len(existing_creeps) + i
                    ), {'memory': {'role': 'harvester'}})
                    break

    @staticmethod
    def run_creep(creep):
        console.log('cannot run undefined creep')


class Harvester(Creeps):
    role = 'harvester'

    @staticmethod
    def factory(spawn):
        creep_type = (LargeHarvester if spawn.room.energyAvailable >= 350 else SmallHarvester)()
        console.log('spawning new {} creep'.format(creep_type.role))
        creep_type.create(spawn)

    @staticmethod
    def run_creep(creep):
        harvester.run_harvester(creep)


class SmallHarvester(Harvester):
    body_composition = [WORK, CARRY, MOVE, MOVE]


class LargeHarvester(Harvester):
    body_composition = [WORK, CARRY, CARRY, MOVE, MOVE, MOVE]
