from .config import config

def Challenge(challenge_id, API_KEY):
    if challenge_id in config['challenges'].keys():
        return config['challenges'][challenge_id]['class'](API_KEY, config)
    else:
        #It is most possibly a crowdAI Generic Challenge
        challenge = config['challenges']['crowdAIGenericChallenge']['class'](API_KEY, challenge_id, config)
        return challenge

def test():
    """
        Placeholder function to test the scaffold.
    """
    return ('Working !!')
