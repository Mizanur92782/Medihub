from django.core.cache import cache
import httpx
import logging

from cache.ttl import CacheTTL

logger = logging.getLogger(__name__)


class CacheManager:

    @staticmethod
    def GetCache(key):

        # Get cache data using key
        data = cache.get(key)

        # Check if data does not exist in cache
        if data is None:
            logger.warning(f"Cache Miss: {key}")

            return {
                "success": False
            }

        logger.info(f"Cache Hit: {key}")

        return {
            "success": True,
            "data": data
        }

    @staticmethod
    def SetCache(key, value, ttl=CacheTTL.SMALL):

        # Random TTL to avoid cache avalanche
        rand_ttl = CacheTTL.RandomTTL(ttl)

        try:
            # Set cache
            cache.set(key, value, timeout=rand_ttl)

            logger.info(f"Cache Set: {key}")

            return {
                "success": True
            }
            
        except Exception as e:
            logger.exception(f"Cache set failed: {key}")

            return {
                "success": False,
                "error": str(e)
            }
            
            
    @staticmethod
    def DeleteCache(key):
        cache.delete(key)
        logger.warning(f"Cache Delete : {key}")