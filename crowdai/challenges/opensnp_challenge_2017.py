from .base_challenge import BaseChallenge

class OpenSNPChallenge2017(BaseChallenge):
    def __init__(self, api_key, config):
        self.challenge_id = "OpenSNPChallenge2017"
        super(OpenSNPChallenge2017, self).__init__(self.challenge_id, api_key, config)
        self.AGGREGATED_PROGRESS_BAR = True
        self._connect()
        self._authenticate()

    def submit(self, data, dry_run=False):
        # Submit final score
        # Close socket.io connection
        return self.execute_function('submit', [data])[0]
