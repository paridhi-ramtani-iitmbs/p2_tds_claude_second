"""
Request validation
"""
from app.config import settings
import hmac

def validate_request(secret: str) -> bool:
    """Validate secret key"""
    try:
        return hmac.compare_digest(secret, settings.SECRET_KEY)
    except:
        return False
