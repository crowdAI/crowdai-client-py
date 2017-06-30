import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/challenges/")


from .challenges.opensnp_challenge_2017 import OpenSNPChallenge2017

config = {
    'remote_host' : 'grader.crowdai.org',
    'remote_port' : 80,
    'TIMEOUT_AUTHENTICATE' : 10,
    'challenges' : {
        'OpenSNPChallenge2017': {
            "class": OpenSNPChallenge2017,
            "TIMEOUT_EXECUTION" : 20000
            }
    }
}
