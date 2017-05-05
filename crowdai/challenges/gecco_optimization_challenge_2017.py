from base_challenge import BaseChallenge

class GeccoOptimizationChallenge2017(BaseChallenge):
    def __init__(self, api_key, config):
        self.challenge_id = "GeccoOptimizationChallenge2017"
        super(GeccoOptimizationChallenge2017, self).__init__(self.challenge_id, api_key, config)
        self._connect()
        self._authenticate()

    def evaluate(self, data, dry_run=False):
        return self.execute_function('evaluate', data)

    def submit(self, data, dry_run=False):
        # Submit final score
        # Close socket.io connection
        return self.execute_function('submit', data)
