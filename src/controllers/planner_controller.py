from defs import *
from planners.resource_planner import ResourcePlanner

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class PlannerController(object):
    @staticmethod
    def run():
        if Game.time % 10 == 0:
            ResourcePlanner.main()
