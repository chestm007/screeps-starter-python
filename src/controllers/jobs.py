from defs import *

__pragma__('noalias', 'name')
__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class JobController:
    REPAIR = 'repair'
    BUILD = 'build'
    CARRY = 'carry'
    MINE = 'mine'
    HARVEST = 'harvest'
    UPGRADE = 'upgrade'

    def __init__(self, memory):
        self.creeps = memory.creeps  # type: list
        self.jobs = memory.jobs  # type: list
        self.rooms = memory.rooms  # type:list
        self.scan_interval = memory.job_controller.scan_interval

    def run(self):
        if Game.time % self.scan_interval == 0:
            self._scan_for_work()
        if len(self.jobs) > 0:
            self._assign_jobs(self._get_jobless_creeps())

    def _assign_jobs(self, jobless_creeps):
        for creep in jobless_creeps:
            if creep.role == self.UPGRADE:
                creep.assign_job(self._get_upgrade_job(self.rooms[creep.room]))
            if creep.role == self.MINE:
                creep.assign_job(self._get_mine_job(self.rooms[creep.room]))
            if len(self.jobs) <= 0:
                return
            for job in [job for job in self.jobs if creep.role == job.name]:
                creep.assign_job(self.jobs.pop(job))

    def _get_jobless_creeps(self):
        return [creep for creep in self.creeps if creep.job is None]

    def _scan_for_work(self):
        # get oldest room based on scan time
        room = sorted(self.rooms, lambda r: r.last_job_scan)[0]

        # get a list of all existing jobs
        existing_structure_jobs = [creep.job.destination for creep in self.creeps]
        unassigned_structure_jobs = [job.destination for job in self.jobs]

        # REPAIR
        structures = [struct for struct in Game.rooms[room].find(FIND_STRUCTURES)
                      if struct.id not in existing_structure_jobs
                      and struct.id not in unassigned_structure_jobs
                      and struct.hits < struct.hitsMax / 2]
        for struct in structures:
            if struct.structureType in [STRUCTURE_CONTAINER, STRUCTURE_ROAD]:
                self._queue_job(self.REPAIR, struct.id, struct.pos.findClosestByPath(STRUCTURE_CONTAINER))

        # BUILD
        construction_sites = [struct for struct in Game.rooms[room].find(FIND_CONSTRUCTION_SITES)
                              if struct.id not in existing_structure_jobs
                              and struct.id not in unassigned_structure_jobs]
        for struct in construction_sites:
            self._queue_job(self.BUILD, struct.id, struct.pos.findClosestByPath(STRUCTURE_CONTAINER))

    def _get_upgrade_job(self, room):
        source = (room.controller.container or
                  Game.getObjectById(room.controller).pos.findClosestByPath(STRUCTURE_CONTAINER))
        return self.job_factory(self.UPGRADE, source, room.controller)

    def _get_mine_job(self, room):
        for source in room:
            if not source.miner:
                return self.job_factory(self.MINE, source.id, source.container)
        pass

    def job_factory(self, job, *args):
        if job == self.REPAIR:
            return RepairJob(*args)
        elif job == self.BUILD:
            return BuildJob(*args)
        elif job == self.CARRY:
            return CarryJob(*args)
        elif job == self.MINE:
            return MineJob(*args)
        elif job == self.HARVEST:
            return HarvestJob(*args)
        elif job == self.UPGRADE:
            return UpgradeJob(*args)
        else:
            console.log('unrecognized job type {}'.format(job))

    def _queue_job(self, job_type, source, destination, interruptable=False):
        self.jobs.append(self.job_factory(job_type, source, destination))
        Memory.jobs.push({'name': job_type,
                          'source': source,
                          'destination': destination,
                          'interruptable': interruptable})


class Job:
    def __init__(self, source, destination, interruptable=False, stage=None):
        self.source = Game.getObjectById(source)
        self.destination = Game.getObjectById(destination)
        self.interruptable = interruptable
        self.stage = stage

    def run(self, creep):
        if not self.stage:
            self.stage = 1
        elif self.stage == 1:
            self.stage_one(creep)
        elif self.stage == 2:
            self.stage_two(creep)

    def _set_stage(self, creep, stage):
        creep.memory.job.stage = stage
        self.stage = stage

    def stage_two(self, creep):
        pass

    def stage_one(self, creep):
        pass

    def _withdraw_from_container(self, creep):
        if 
        if self.source.structureType == STRUCTURE_CONTAINER:
            res = creep.withdraw(self.source, RESOURCE_ENERGY)
            if res == ERR_NOT_IN_RANGE:
                creep.moveTo(self.source)
                creep.withdraw(self.source, RESOURCE_ENERGY)
            elif res == ERR_NOT_ENOUGH_ENERGY:
                pass
            elif res != OK:
                console.log('{} cannot withdraw from {} {}'.format(creep.memory.role, self.source.structureType, res))
            elif res == OK:
                self._set_stage(creep, 2)

    def _upgrade_controller(self, creep):
        if creep.pos.inRangeTo(self.destination, 3):
            result = creep.upgradeController(self.destination)
            if result != OK:
                console.log("[{}] Unknown result from creep.upgradeController({}): {}".format(
                    creep.name, self.destination, result))
                del creep.memory.job
            # Let the creeps get a little bit closer than required to the controller, to make room for other creeps.
            if not creep.pos.inRangeTo(self.destination, 2):
                creep.moveTo(self.destination)

    def _harvest_energy(self, creep):
        result = creep.harvest(self.source)
        if result == ERR_NOT_IN_RANGE:
            creep.moveTo(self.source)
        elif result == ERR_NOT_ENOUGH_ENERGY:
            return
        elif result != OK:
            console.log("[{}] Unknown result from creep.harvest({}): {}".format(creep.name, self.source, result))
            del creep.memory.job
        return result


class RepairJob(Job):
    def stage_one(self, creep):
        self._withdraw_from_container(creep)

    def stage_two(self, creep):
        if self.destination.hits >= self.destination.hitsMax / 3 * 2:
            del creep.memory.job
        res = creep.repair(self.destination)
        if res == ERR_NOT_IN_RANGE:
            creep.moveTo(self.destination)
            creep.repair(self.destination)
            return


class BuildJob(Job):
    def stage_one(self, creep):
        self._withdraw_from_container(creep)

    def stage_two(self, creep):
        res = creep.build(self.destination)
        if res == ERR_NOT_IN_RANGE:
            creep.moveTo(self.destination)
            creep.build(self.destination)
            return
        elif res == OK:
            return
        del creep.memory.job


class CarryJob(Job):
    def stage_one(self, creep):
        self._withdraw_from_container(creep)

    def stage_two(self, creep):
        result = creep.transfer(self.destination, RESOURCE_ENERGY)
        if result == OK or result == ERR_NOT_IN_RANGE:
            del creep.memory.job
        else:
            console.log("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                creep.name, self.destination, RESOURCE_ENERGY, result))
            del creep.memory.job


class MineJob(Job):
    def stage_one(self, creep):
        result = self._harvest_energy(creep)
        if result == OK:
            creep.drop(RESOURCE_ENERGY)

    def stage_two(self, creep):
        pass


class HarvestJob(Job):
    def stage_one(self, creep):
        self._harvest_energy(creep)

    def stage_two(self, creep):
        if self.destination.energyCapacity:
            if creep.pos.isNearTo(self.destination):
                result = creep.transfer(self.destination, RESOURCE_ENERGY)
                if result == OK or result == ERR_NOT_IN_RANGE:
                    del creep.memory.job
                else:
                    console.log("[{}] Unknown result from creep.transfer({}, {}): {}".format(
                        creep.name, self.destination, RESOURCE_ENERGY, result))
                    del creep.memory.job
        else:
            self._upgrade_controller(creep)


class UpgradeJob(Job):
    def stage_one(self, creep):
        self._withdraw_from_container(creep)

    def stage_two(self, creep):
        self._upgrade_controller(creep)
