
class UserSignupCacheKeys:
    """Cache keys for user signup process."""

    @staticmethod
    def user_register_key(email: str) -> str:
        """Generate cache key for user registration."""
        return f"user_signup:register:{email}"