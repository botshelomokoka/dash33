from typing import Optional, Dict, Any

class Dash33Error(Exception):
    """Base exception class for dash33"""
    def __init__(self, message: str, code: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.code = code
        self.details = details or {}

class WalletError(Dash33Error):
    """Wallet-related errors"""
    pass

class AIError(Dash33Error):
    """AI/ML-related errors"""
    pass

class SecurityError(Dash33Error):
    """Security-related errors"""
    pass

class ValidationError(Dash33Error):
    """Data validation errors"""
    pass

class NetworkError(Dash33Error):
    """Network communication errors"""
    pass

def handle_error(error: Exception) -> Dict[str, Any]:
    """Convert exceptions to API-friendly responses"""
    if isinstance(error, Dash33Error):
        return {
            "error": {
                "code": error.code,
                "message": str(error),
                "details": error.details
            }
        }
    return {
        "error": {
            "code": "INTERNAL_ERROR",
            "message": "An unexpected error occurred",
            "details": {"original_error": str(error)}
        }
    }
