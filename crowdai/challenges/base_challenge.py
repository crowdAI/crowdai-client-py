from socketIO_client import SocketIO, LoggingNamespace

class BaseChallengeException(Exception):
    pass

class CrowdAIAuthenticationError(BaseChallengeException):
    pass

class CrowdAIExecuteFunctionError(BaseChallengeException):
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
            # TO-DO: Log authentication error
            raise CrowdAIAuthenticationError(args["message"])

    def _authenticate(self):
        print "Beginning Authenticating :", self.challenge_id, self.api_key
        self.session_key = None
        self.socketio.emit('authenticate', {"API_KEY":self.api_key,
                                       "challenge_id": self.challenge_id},
                                       self._authenticate_response)
        self.socketio.wait_for_callbacks(seconds=self.config['TIMEOUT_AUTHENTICATE'])
        if self.session_key == None:
            # TO-DO: Log authentication error
            raise CrowdAIAuthenticationError("Authentication Timeout")
        else:
            print "Authentication successful :: Token :: ", self.session_key
            # TO-DO: Log authentication successful

    def on_execute_function_response(self, args):
        if args["status"] == True:
            self.execute_function_response = args
        else:
            # TO-DO: Log Challenge Error
            raise CrowdAIExecuteFunctionError(args["message"])

    def execute_function(self, function_name, data, dry_run=False):
        #TO-DO : Validate if authenticated
        self.execute_function_response = None
        self.socketio.emit('execute_function',
                        {   "session_token": self.session_key,
                            "challenge_id": self.challenge_id,
                            "function_name": function_name,
                            "data": data,
                            "dry_run" : dry_run
                        }, self.on_execute_function_response)
        self.socketio.wait_for_callbacks(seconds=self.config['challenges'][self.challenge_id]["TIMEOUT_EXECUTION"])
        if self.execute_function_response == None:
            raise CrowdAIExecuteFunctionError("Evaluation Request Timeout")
            # print "Evaluation Request Timed Out..."
        else:
            return self.execute_function_response["response"]
