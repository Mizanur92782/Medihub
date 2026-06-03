
class CacheKeys:

    VERSION = 'v1'

    @staticmethod
    def UserProfile(user_id):
        return f"user:{CacheKeys.VERSION}:{user_id}:profile"

    @staticmethod
    def UserPost(user_id):
        if user_id:
            return f"post:{CacheKeys.VERSION}:{user_id}"
        return f"post:{CacheKeys.VERSION}"

    @staticmethod
    def DoctorFeed(user_id, division=None, district=None, specialization=None):
        return (
            f"feed:{CacheKeys.VERSION}:{user_id}"
            f":div_{division or 'all'}"
            f":dis_{district or 'all'}"
            f":spec_{specialization or 'all'}"
        )