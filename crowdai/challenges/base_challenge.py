from socketIO_client import SocketIO, LoggingNamespace
import uuid
from crowdai_errors import *

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
            print args
        else:
            raise CrowdAIExecuteFunctionError(args["message"])

    def on_execute_function_response_complete(self, args):
        """
            Placeholder function to be able to account for
            Timeout thresholds
        """
        pass

    def execute_function(self, function_name, data, dry_run=False):
        #TO-DO : Validate if authenticated
        self.response_channel = self.challenge_id+"::"+str(uuid.uuid4())
        #Prepare for response

        #NOTE: response_channel is prepended with the session_key to discourage hijacking attempts
        self.socketio.on(self.session_key+"::"+self.response_channel, self.on_execute_function_response)
        self.execute_function_response = None
        self.socketio.emit('execute_function',
                        {   "response_channel" : self.response_channel,
                            "session_token": self.session_key,
                            "api_key": self.api_key,
                            "challenge_id": self.challenge_id,
                            "function_name": function_name,
                            "data": data,
                            "dry_run" : dry_run
                        }, self.on_execute_function_response_complete)

        #TO-DO: Loop till execute_function_response is not valid

        self.socketio.wait_for_callbacks(seconds=self.config['challenges'][self.challenge_id]["TIMEOUT_EXECUTION"])
        #if self.execute_function_response == None:
        #    raise CrowdAIExecuteFunctionError("Evaluation Request Timeout")
        #    # print "Evaluation Request Timed Out..."
        #else:
        #    response = self.execute_function_response
        #    return response["response"]
