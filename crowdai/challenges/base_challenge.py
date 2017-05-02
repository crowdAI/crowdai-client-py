class BaseChallenge(object):
    def __init__(self, challenge_id, api_key, config):
        self.api_key = api_key
        self.challenge_id = challenge_id
        self.config = config
        self.session_key = "None"

    def _connect(self):
        # self.socketio =
        pass
        
    def _authenticate(self):
        print "Authenticating :", self.challenge_id, self.api_key
        return True
