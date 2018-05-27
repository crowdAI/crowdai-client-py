import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(os.path.abspath(__file__))+"/challenges/")

from .challenges.opensnp_challenge_2017 import OpenSNPChallenge2017
from .challenges.criteo_ad_placement_challenge_nips_2017 import CriteoAdPlacementNIPS2017
from .challenges.learning_2_run_challenge_nips_2017 import Learning2RunChallengeNIPS2017
from .challenges.ai_generated_music_challenge import AIGeneratedMusicChallenge
from .challenges.www_musical_genre_challenge import WWWMusicalGenreRecognitionChallenge
from .challenges.kit_energy_challenge import KITEnergyChallenge
from .challenges.ieee_investment_ranking_challenge import IEEEInvestmentRankingChallenge
from .challenges.crowdai_mapping_challenge import crowdAIMappingChallenge
from .challenges.crowdai_generic_challenge import crowdAIGenericChallenge

config = {
    'remote_host': 'grader.crowdai.org',
    'remote_port': 80,
    'TIMEOUT_AUTHENTICATE': 10,
    'challenges': {
        'OpenSNPChallenge2017': {
            "class": OpenSNPChallenge2017,
            "TIMEOUT_EXECUTION": 20000
            },
        'CriteoAdPlacementNIPS2017': {
            "class": CriteoAdPlacementNIPS2017,
            "TIMEOUT_EXECUTION": 20000
        },
        'Learning2RunChallengeNIPS2017': {
            "class": Learning2RunChallengeNIPS2017,
            "TIMEOUT_EXECUTION": 20000
        },
        'AIGeneratedMusicChallenge': {
            "class": AIGeneratedMusicChallenge,
            "TIMEOUT_EXECUTION": 20000
        },
        'WWWMusicalGenreRecognitionChallenge': {
            "class": WWWMusicalGenreRecognitionChallenge,
            "TIMEOUT_EXECUTION": 20000
        },
        'KITEnergyChallenge': {
            "class": KITEnergyChallenge,
            "TIMEOUT_EXECUTION": 20000
        },
        'IEEEInvestmentRankingChallenge' : {
            "class" : IEEEInvestmentRankingChallenge,
            "TIMEOUT_EXECUTION": 20000
        },
        'crowdAIMappingChallenge' : {
            "class" : crowdAIMappingChallenge,
            "TIMEOUT_EXECUTION": 20000
        },
        'crowdAIGenericChallenge' : {
            "class" : crowdAIGenericChallenge,
            "TIMEOUT_EXECUTION": 20000
        }
    },
    'crowdai_remote_api': 'https://www.crowdai.org/api/external_graders/'
}
