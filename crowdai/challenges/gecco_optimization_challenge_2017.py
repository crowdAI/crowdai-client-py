from .base_challenge import BaseChallenge

class GeccoOptimizationChallenge2017(BaseChallenge):
    def __init__(self, api_key, config):
        self.challenge_id = "GeccoOptimizationChallenge2017"
        super(GeccoOptimizationChallenge2017, self).__init__(self.challenge_id, api_key, config)
        self.AGGREGATED_PROGRESS_BAR = True
        self._connect()
        self._authenticate()

    def evaluate_parallel(self, data, dry_run=False):
        return self.execute_function('evaluate', data, parallel=True)

    def evaluate(self, data, dry_run=False):
        return self.execute_function('evaluate', data, parallel=False)

    def submit(self, data, dry_run=False):
        # Submit final score
        # Close socket.io connection
        return self.execute_function('submit', data)
