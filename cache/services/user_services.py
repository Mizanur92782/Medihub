from cache.keys import CacheKeys
from authentication.services import logger
from cache.manager import CacheManager
from cache.ttl import CacheTTL

class UserProfileCacheServies:
    
    @staticmethod
    def GetProfile(user_id):
        key = CacheKeys.UserProfile(user_id)
        result = CacheManager.GetCache(key)
        return result['data'] if result['success'] else None

    @staticmethod
    def SetProfile(user_id, data):
        key = CacheKeys.UserProfile(user_id)
        CacheManager.SetCache(key, data, CacheTTL.RandomTTL(CacheTTL.SMALL, 30))
        
        
    @staticmethod
    def ClearProfile(user_id):
        key = CacheKeys.UserProfile(user_id)
        CacheManager.DeleteCache(key)