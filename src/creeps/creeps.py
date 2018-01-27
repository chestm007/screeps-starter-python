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
    def _recycle_creep_name(role):
        for creep_name in Object.keys(Memory.creeps):
            if not Object.keys(Game.creeps).includes(creep_name):
                return creep_name
        existing_creeps = []
        for name in Object.keys(Game.creeps):
            if name.startswith(role):
                existing_creeps.append(name)
            i = 0
            while True:
                new_name = '{}{}'.format(role, i)
                if existing_creeps.includes(new_name):
                    i += 1
                else:
                    creep_name = new_name
                    break
            return creep_name

    @staticmethod
    def create(body, spawn, role):
        if body is None:
            console.log('Error creating {}: no defined body composition'.format(role))
        else:
            spawn.createCreep(body, Creeps._recycle_creep_name(role), {'memory': {'role': 'harvester'}})

    @staticmethod
    def run_creep(creep):
        console.log('cannot run undefined creep')