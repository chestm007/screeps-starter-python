from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class Creeps(object):
    body_composition = None
    body_part_cost = {
        MOVE: 50,
        WORK: 100,
        CARRY: 50,
        ATTACK: 80,
        RANGED_ATTACK: 150,
        HEAL: 250,
        TOUGH: 10,
        CLAIM: 600
    }

    num_creep_to_size = ['small', 'small', 'medium', 'medium', 'large', 'xlarge']
    @staticmethod
    def _calculate_creation_cost(body_composition):
        return sum([Creeps.body_part_cost[part] for part in body_composition])

    @staticmethod
    def factory(spawn, num_workers):
        pass

    @staticmethod
    def create(body, spawn, role):
        if body is None:
            console.log('Error creating {}: no defined body composition'.format(role))
        else:
            existing_creeps = []
            for name in Object.keys(Game.creeps):
                if name.startswith(role):
                    existing_creeps.append(name)
            i = 0
            while True:
                if existing_creeps.includes('{}{}'.format(role, (len(existing_creeps) + i))):
                    i += 10
                else:
                    spawn.createCreep(body, '{type}{number}'.format(
                        type=role,
                        number=len(existing_creeps) + i
                    ), {'memory': {'role': 'harvester'}})
                    break

    @staticmethod
    def run_creep(creep):
        console.log('cannot run undefined creep')