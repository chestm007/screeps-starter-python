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


class Claimer(Worker):
    role = 'claimer'

    body_composition = [
        [CLAIM, CLAIM, MOVE, MOVE]
    ]

    def run_creep(self):
        return