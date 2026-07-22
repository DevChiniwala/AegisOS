class AegisError(Exception):
    """Base exception for AegisOS"""
    pass

class TransactionError(AegisError):
    pass

class EntityNotFoundError(AegisError):
    pass

class ScoringError(AegisError):
    pass

class AuthenticationError(AegisError):
    pass

class AuthorizationError(AegisError):
    pass

class ValidationError(AegisError):
    pass

class ConfigurationError(AegisError):
    pass

class DatabaseError(AegisError):
    pass

class EventBusError(AegisError):
    pass

class ModelError(AegisError):
    pass
