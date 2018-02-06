from defs import *

__pragma__('noalias', 'undefined')
__pragma__('noalias', 'Infinity')
__pragma__('noalias', 'keys')
__pragma__('noalias', 'name')
__pragma__('noalias', 'get')
__pragma__('noalias', 'set')
__pragma__('noalias', 'type')
__pragma__('noalias', 'update')


class PathCache:
    def __init__(self):
        if not Memory.path_cache:
            Memory.path_cache = {}
        self.cache = Memory.path_cache

    def add_path(self, _from: RoomPosition, to: RoomPosition, path) -> None:
        """
        add path to cache
        """
        key = self.get_path_key(_from, to)

        cached_path = {'path': path,
                       'uses': 1}
        self.cache[key] = cached_path

    def get_path(self, _from: RoomPosition, to: RoomPosition) -> list:
        """
        will attempt to load path from cache, will add new path to cache if one
        is not found
        """
        cached_path = self.cache[self.get_path_key(_from, to)]
        if cached_path:
            cached_path.uses += 1
            return cached_path
        else:
            path = _from.findPathTo(to, {'ignoreCreeps': True})
            if path:
                self.add_path(_from, to, path)
                return path

    def clean_cache(self) -> None:
        """
        clean the cache, starting at paths with only 1 use, working up too as
        many are required until cache is at the desired size
        """
        self.clean_cache_by_usage(1)

    def clean_cache_by_usage(self, usage: int) -> None:
        if _.size(self.cache) > 1500:  # ~150kb
            console.log('Cleaning path cache (usage == '+str(usage)+')...')
            counter = 0
            for key in Object.keys(self.cache):
                cached = self.cache[key]
                if cached.uses == usage:
                    del self.cache[key]
                    counter += 1
            Game.notify('Path cache of usage '+str(usage)+' cleaned! '+counter+' paths removed', 6 * 60)
            self.clean_cache_by_usage(usage + 1)

    def show_cache_usage(self) -> None:
        usage_count_counter = {}
        how_many_times_cache_used = 0
        for key in Object.keys(self.cache):
            cached = self.cache[key]
            usage_count_counter['used'+cached.uses] = usage_count_counter['used'+cached.uses] + 1 or 1
            how_many_times_cache_used += cached.uses
        console.log(JSON.stringify(usage_count_counter))
        console.log('howManyTimesCacheUsed: ' + how_many_times_cache_used)
        console.log('cache size: ' + str(_.size(self.cache)))

    def get_path_key(self, _from: RoomPosition, to: RoomPosition) -> str:
        return self.get_pos_key(_from) + '$' + self.get_pos_key(to)

    @staticmethod
    def get_pos_key(pos: RoomPosition) -> str:
        return str(pos.x) + 'x' + str(pos.y) + pos.roomName
