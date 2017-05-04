from socketIO_client import SocketIO, LoggingNamespace

class BaseChallengeException(Exception):
    pass

class CrowdAIAuthenticationError(BaseChallengeException):
    pass

class BaseChallenge(object):
    def __init__(self, challenge_id, api_key, config):
        self.api_key = api_key
        self.challenge_id = challenge_id
        self.config = config
        self.session_key = None

    def _connect(self):
        self.socketio = SocketIO(self.config['remote_host'], self.config['remote_port'], LoggingNamespace)

    def _authenticate_response(self, args):
        if args["status"] == True:
            self.session_key = args["session_token"]
        else:
            raise CrowdAIAuthenticationError(args["message"])

    def _authenticate(self):
        print "Beginning Authenticating :", self.challenge_id, self.api_key
        self.socketio.emit('authenticate', {"API_KEY":self.api_key,
                                       "challenge_id": self.challenge_id},
                                       self._authenticate_response)
        self.socketio.wait_for_callbacks(seconds=self.config['TIMEOUT_AUTHENTICATE'])
        if self.session_key == None:
            print "Authentication timeout..."
        else:
            print "Authentication successful :: Token :: ", self.session_key
            # TO-DO: Raise Error
