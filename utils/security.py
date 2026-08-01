from fastapi import HTTPException, status
from config.settings import settings
from utils.logger import logger

class SecurityGuard:
    """
    Enforces security policies and user confirmation requirements
    for critical system operations like file deletion, system shutdown,
    restart, or registry modifications.
    """
    
    @staticmethod
    def verify_action_confirmation(action: str, confirmed: bool, details: str = "") -> None:
        """
        Verifies if an action requiring confirmation is explicitly confirmed by user.
        Raises HTTP 403 Forbidden if confirmation is required but missing.
        """
        if settings.require_confirmation and not confirmed:
            logger.warning(f"[SecurityGuard] Action blocked: '{action}' requires explicit confirmation. Details: {details}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "ConfirmationRequired",
                    "action": action,
                    "details": details,
                    "message": f"Action '{action}' is a restricted operation and requires explicit user confirmation (`confirmed: true`)."
                }
            )
        logger.info(f"[SecurityGuard] Action authorized: '{action}'. Details: {details}")

security_guard = SecurityGuard()
