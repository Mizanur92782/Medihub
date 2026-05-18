
class CacheKeys:
    
    VERSION='v1'
    
    
    @staticmethod
    def UserProfile(user_id):
        return f"user:{CacheKeys.VERSION}:{user_id}:profile"
    
    @staticmethod
    def UserPost(user_id):
        if user_id:
            return f"post:{CacheKeys.VERSION}:{user_id}"
        return f"post:{CacheKeys.VERSION}"