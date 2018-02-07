from defs import *
from layouts.base_layout import BaseLayout

__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'name')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')

EX = STRUCTURE_EXTENSION
RD = STRUCTURE_ROAD
SP = STRUCTURE_SPAWN
ST = STRUCTURE_STORAGE
LI = STRUCTURE_LINK
TO = STRUCTURE_TOWER
LA = STRUCTURE_LAB
NO = None
RA = STRUCTURE_RAMPART
CO = STRUCTURE_CONTAINER
TE = STRUCTURE_TERMINAL
OB = STRUCTURE_OBSERVER


class DiamondLayout:
    layers = {
        'base': [
            [NO, NO, NO, NO, EX, EX, EX, NO, NO, NO, NO],
            [NO, NO, NO, EX, EX, RD, EX, EX, NO, NO, NO],
            [NO, NO, EX, EX, RD, EX, RD, EX, EX, NO, NO],
            [NO, EX, EX, RD, EX, EX, EX, RD, EX, EX, NO],
            [EX, EX, RD, EX, EX, EX, CO, EX, RD, EX, EX],
            [RD, RD, EX, EX, EX, LI, EX, EX, EX, RD, NO],
            [EX, EX, RD, EX, CO, EX, EX, EX, RD, EX, EX],
            [NO, EX, EX, RD, EX, EX, EX, RD, EX, EX, NO],
            [NO, NO, EX, EX, RD, EX, RD, EX, EX, NO, NO],
            [NO, NO, NO, EX, EX, RD, EX, EX, NO, NO, NO],
            [NO, NO, NO, NO, EX, EX, EX, NO, NO, NO, NO]],
    }

class BonzaiBunker:
    layers = {
        'base': [
            [NO, RD, RD, EX, EX, RD, RD, RD, EX, RD, RD, RD, NO],
            [RD, LI, EX, EX, RD, EX, EX, EX, RD, EX, EX, LI, RD],
            [RD, EX, EX, RD, EX, RD, EX, RD, EX, RD, EX, EX, RD],
            [RD, EX, RD, EX, EX, EX, RD, EX, EX, EX, RD, EX, EX],
            [EX, RD, EX, EX, TO, RD, SP, CO, TO, EX, EX, RD, EX],
            [EX, EX, RD, EX, CO, NO, TO, NO, RD, EX, RD, EX, RD],
            [RD, EX, EX, RD, SP, TO, ST, RD, LI, RD, EX, EX, RD],
            [RD, EX, RD, EX, RD, NO, TO, NO, RD, NO, RD, NO, RD],
            [EX, RD, EX, EX, TO, CO, SP, RD, TE, LA, NO, RD, NO],
            [RD, EX, RD, EX, EX, EX, RD, NO, LA, LA, RD, NO, RD],
            [RD, EX, EX, RD, EX, RD, EX, RD, LA, RD, LA, NO, NO],
            [RD, OB, EX, EX, RD, EX, EX, NO, RD, LA, LA, NO, RD],
            [NO, RD, RD, RD, EX, EX, RD, RD, NO, RD, RD, RD, NO]],
        'ramparts': [
            [NO, RA, RA, RA, RA, RA, RA, RA, RA, RA, RA, RA, NO],
            [RA, RA, RA, RA, RA, RA, RA, RA, RA, RA, RA, RA, RA],
            [RA, RA, RA, RA, RA, RA, RA, RA, RA, RA, RA, RA, RA],
            [RA, RA, RA, RA, NO, NO, NO, NO, NO, RA, RA, RA, RA],
            [RA, RA, RA, NO, NO, NO, NO, NO, NO, NO, RA, RA, RA],
            [RA, RA, RA, NO, NO, NO, NO, NO, NO, NO, RA, RA, RA],
            [RA, RA, RA, NO, NO, NO, NO, NO, NO, NO, RA, RA, RA],
            [RA, RA, RA, NO, NO, NO, NO, NO, NO, NO, RA, RA, RA],
            [RA, RA, RA, RA, NO, NO, NO, NO, NO, RA, RA, RA, RA],
            [RA, RA, RA, RA, RA, RA, RA, RA, RA, RA, RA, RA, RA],
            [RA, RA, RA, RA, RA, RA, RA, RA, RA, RA, RA, RA, RA],
            [NO, RA, RA, RA, RA, RA, RA, RA, RA, RA, RA, RA, NO],
            [RA, RA, RA, NO, NO, NO, NO, NO, NO, NO, RA, RA, RA],
        ]
    }
