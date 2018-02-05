from creeps.worker import Worker, Harvester, Claimer
from defs import STRUCTURE_ROAD, STRUCTURE_CONTAINER, ERR_NOT_IN_RANGE, OK, Game, STRUCTURE_SPAWN, \
    FIND_CONSTRUCTION_SITES, Object, _


class Builder(Worker):
    role = 'builder'

    def run_creep(self):
        if self._should_be_harvester():
            self._become_harvester()
            Harvester.run_creep(self)
            return

        self._pre_run_checks()

        if self.creep.memory.filling:
            self._harvest_source(self._get_source())

        else:
            target = self._get_target()
            if target:
                if not target:
                    del self.creep.memory.target
                    return
                if target.structureType == STRUCTURE_ROAD or target.structureType == STRUCTURE_CONTAINER:
                    if target.hits >= target.hitsMax / 3 * 2:
                        del self.creep.memory.target
                        self._get_target()
                    res = self.creep.repair(target)
                    if res == ERR_NOT_IN_RANGE:
                        self.creep.moveTo(target)
                        return
                    elif res == OK:
                        return
                res = self.creep.build(target)
                if res == ERR_NOT_IN_RANGE:
                    self.creep.moveTo(target)
                    return
                elif res == OK:
                    return
            del self.creep.memory.target

    def _get_target(self):
        target = None
        if self.creep.memory.target:
            target = Game.getObjectById(self.creep.memory.target)
        else:
            if self.creep.memory.source:
                target = self.get_closest_to_creep(
                    self.structures_in_room.filter(lambda s: s.hits < s.hitsMax / 2)
                )
            if not target:
                target = self.get_closest_to_creep(
                    self.construction_sites_in_room.filter(
                        lambda s: s.structureType == STRUCTURE_SPAWN
                    )
                )
            if not target:
                target = self.creep.pos.findClosestByRange(FIND_CONSTRUCTION_SITES)
            if target:
                self.creep.memory.target = target.id
            claimers = [Game.creeps[creep] for creep in Object.keys(Game.creeps)
                        if Game.creeps[creep].memory.role == Claimer.role]
            for claimer in claimers:
                unbuilt_spawn = _(claimer.room.find(FIND_CONSTRUCTION_SITES).filter(
                    lambda s: s.structureType == STRUCTURE_SPAWN
                )).sample()
                if unbuilt_spawn:
                    self.creep.memory.target = unbuilt_spawn.id
                    return unbuilt_spawn
        return target