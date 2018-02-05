from creeps.worker import Worker
from defs import CLAIM, MOVE


class Claimer(Worker):
    role = 'claimer'

    body_composition = [
        [CLAIM, CLAIM, MOVE, MOVE]
    ]

    def run_creep(self):
        return