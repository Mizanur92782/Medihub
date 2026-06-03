import random

class CacheTTL:
    SMALL      = 60
    MEDIUM     = 300
    LARGE      = 1000
    VERY_LARGE = 2000
    DAY        = 86400

    @staticmethod
    def RandomTTL(ttl, jitter=60):
        return ttl + random.randint(0, jitter)
    
        