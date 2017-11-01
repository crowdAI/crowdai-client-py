class BaseChallengeException(Exception):
    pass

class CrowdAIAuthenticationError(BaseChallengeException):
    pass

class CrowdAIExecuteFunctionError(BaseChallengeException):
    pass

class CrowdAIAPINotAvailableError(BaseChallengeException):
    pass

class InvalidFileError(BaseChallengeException):
    pass
