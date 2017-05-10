from .config import config

import sys
import os

sys.path.append(os.path.dirname(os.path.realpath(__file__)))


def Challenge(challenge_id, API_KEY):
    if challenge_id in config['challenges'].keys():
        return config['challenges'][challenge_id]['class'](API_KEY, config)
    else:
        #TO-DO : Do error handling here
        raise Exception("Error :( Unknown challenge_id. Update your client")

def test():
    """
        Placeholder function to test the scaffold.
    """
    return ('Working !!')
