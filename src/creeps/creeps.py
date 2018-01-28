from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class _Creep(Creep):
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

    def _calculate_creation_cost(self, body_composition):
        return sum([self.body_part_cost[part] for part in body_composition])

    @staticmethod
    def create(body, spawn, role):
        if body is None:
            console.log('Error creating {}: no defined body composition'.format(role))
        else:
            spawn.createCreep(body, None, {'memory': {'role': role}})

    def run_creep(self):
        console.log('cannot run undefined creep')

    def factory(self, spawn, num_workers):
        pass
