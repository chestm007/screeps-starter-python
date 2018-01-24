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

    @staticmethod
    def factory(spawn):
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