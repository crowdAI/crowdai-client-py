from challenges.opensnp_challenge_2017 import OpenSNPChallenge2017

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
