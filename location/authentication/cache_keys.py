
class SignupCacheKeys:
    """Cache keys for signup process."""
    @staticmethod
    def SignupEmailVerification(email):
        return f"signup:email_verification:{email}"