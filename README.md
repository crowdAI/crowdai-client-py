# crowdai-client-py
Python client to interact with CrowdAI Grading Server.

# Installation Instruction
```
pip install crowdai
```

```
import sys
import crowdai

api_key = "YOUR-API-KEY-HERE"
challenge = crowdai.Challenge("CHALLENGE_ID", api_key)

data = ...

response = challenge.submit(data)
print response
challenge.disconnect()
```

## Implemented Challenges and associated functions

* OpenSNPChallenge2017
  - `submit` :
    Submit the list of heights for the test set
* CriteoAdPlacementNIPS2017
  - `submit` :
    Submits the path to a prediction file for the [Criteo Ad Placement challenge](https://www.crowdai.org/challenges/nips-17-workshop-criteo-ad-placement-challenge)
* Learning2RunChallengeNIPS2017
  - `submit`:
    Submits a docker tar dump for the [NIPS 2017: Learning to Run Challenge]
* AIGeneratedMusicChallenge
  - `submit`:
    Submits a midi file of length 3600 seconds (at 120 bpm) to the grading interface
* KITEnergyChallenge
  - `submit`:
    Submits a the forecasts for the problem definition in the KITEnergyChallenge
* IEEEStockPredictionChallenge
  - `submit`:
    Submits a the predictions for the problem definition in the IEEEStockPredictionChallenge

# Author
S.P. Mohanty <sharada.mohanty@epfl.ch>
