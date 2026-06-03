from cache.keys import CacheKeys
from cache.manager import CacheManager
from cache.ttl import CacheTTL


class DoctorFeedCacheService:

    @staticmethod
    def GetFeed(user_id, division=None, district=None, specialization=None):
        key    = CacheKeys.DoctorFeed(user_id, division, district, specialization)
        result = CacheManager.GetCache(key)
        return result["data"] if result["success"] else None

    @staticmethod
    def SetFeed(user_id, data, division=None, district=None, specialization=None):
        key = CacheKeys.DoctorFeed(user_id, division, district, specialization)
        CacheManager.SetCache(key, data, CacheTTL.DAY)

    @staticmethod
    def ClearFeed(user_id, division=None, district=None, specialization=None):
        key = CacheKeys.DoctorFeed(user_id, division, district, specialization)
        CacheManager.DeleteCache(key)
