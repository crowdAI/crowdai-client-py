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



# Author
S.P. Mohanty <sharada.mohanty@epfl.ch>
