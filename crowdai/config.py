from challenges.gecco_optimization_challenge_2017 import GeccoOptimizationChallenge2017

config = {
    'remote_host' : 'iccluster043',
    'remote_port' : 5001,
    'TIMEOUT_AUTHENTICATE' : 10,
    'challenges' : {
        'GeccoOptimizationChallenge2017': {
            "class": GeccoOptimizationChallenge2017,
            "TIMEOUT_EXECUTION" : 20000
            }
    }
}
