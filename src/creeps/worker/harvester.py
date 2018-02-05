from creeps.worker import Worker, Carrier
from creeps.worker.worker import Builder
from defs import Game, Object, STRUCTURE_EXTENSION, STRUCTURE_SPAWN, STRUCTURE_TOWER, _, STRUCTURE_CONTROLLER


class Harvester(Worker):
    role = 'harvester'

    def run_creep(self):
        """
        Runs a creep as a generic harvester.
        """
        if self._should_be_builder():
            self._become_builder()
            Builder.run_creep(self)
            return

        self._pre_run_checks()

        if self.creep.memory.filling:
            self._harvest_source(self._get_source())
        else:
            self._transfer_energy(self._get_target())

    def _get_target(self):
        target = None
        # If we have a saved target, use it
        if self.creep.memory.target:
            target = Game.getObjectById(self.creep.memory.target)
        else:
            # fill extentions and spawns first
            if len([creep for creep in Object.keys(Game.creeps)
                    if Game.creeps[creep].memory.role == Carrier.role]) <= 0:
                target = self.get_closest_to_creep(
                    self.structures_in_room.filter(
                        lambda s: (
                                      s.structureType == STRUCTURE_EXTENSION
                                      or s.structureType == STRUCTURE_SPAWN
                                      or s.structureType == STRUCTURE_TOWER
                                  ) and s.energy < s.energyCapacity
                    ))
            if not target:
                # Get a random new target.
                target = _(self.structures_in_room).filter(
                    lambda s: s.structureType == STRUCTURE_CONTROLLER
                ).sample()
            if target:
                self.creep.memory.target = target.id
        return target