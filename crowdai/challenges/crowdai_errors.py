class BaseChallengeException(Exception):
    pass

class CrowdAIAuthenticationError(BaseChallengeException):
    pass

class CrowdAIExecuteFunctionError(BaseChallengeException):
    pass
