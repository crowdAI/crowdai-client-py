from socketIO_client import SocketIO, LoggingNamespace
import uuid
from crowdai_errors import *
from job_states import JobStates
import json

from tqdm import tqdm
from termcolor import colored, cprint

import pkg_resources


class BaseChallenge(object):
    def __init__(self, challenge_id, api_key, config):
        self.api_key = api_key
        self.challenge_id = challenge_id
        self.config = config
        self.session_key = None
        self.latest_response = False
        self.pbar = None

    def _connect(self):
        self.socketio = SocketIO(self.config['remote_host'], self.config['remote_port'], LoggingNamespace)

    def _authenticate_response(self, args):
        if args["status"] == True:
            self.session_key = args["session_token"]
        else:
            # TO-DO: Log authentication error
            raise CrowdAIAuthenticationError(args["message"])

    def _authenticate(self):
        begin_authentication_message = ""
        begin_authentication_message += colored("CrowdAI.Authentication.Event", "cyan", attrs=['bold'])+":  "
        begin_authentication_message += "Authenticating for challenge = "
        begin_authentication_message += colored(self.challenge_id, "blue", attrs=['bold', 'underline'])
        print begin_authentication_message

        self.session_key = None
        self.socketio.emit('authenticate', {"API_KEY":self.api_key,
                                           "challenge_id": self.challenge_id,
                                           "client_version":pkg_resources.get_distribution("crowdai").version},
                                           self._authenticate_response)
        self.socketio.wait_for_callbacks(seconds=self.config['TIMEOUT_AUTHENTICATE'])
        if self.session_key == None:
            # TO-DO: Log authentication error
            raise CrowdAIAuthenticationError("Authentication Timeout")
        else:
            # session_key_message = ""
            # session_key_message += colored("CrowdAI.Authentication.Event", "blue", attrs=['bold'])+":  "
            # session_key_message += "session_key="+colored(self.session_key, "blue", attrs=['bold'])
            # print session_key_message
            pass
            # Temporarily ignore printing session_key
            # TO-DO: Log authentication successful

    def on_execute_function_response(self, channel_name, payload):
        payload = json.loads(payload)
        job_state = payload['job_state']
        job_id = payload['job_id']
        if job_state == JobStates.ERROR:
            raise CrowdAIExecuteFunctionError(payload["message"])
        elif job_state == JobStates.ENQUEUED :
            job_event_messsage = ""
            job_event_messsage += colored("CrowdAI.Job.Event", "cyan", attrs=['bold'])+":  "
            job_event_messsage += colored("JOB_ENQUEUED ("+job_id+")", "yellow", attrs=['bold'])

            self.write_above_single_progress_bar(job_event_messsage)

            # job_event_messsage = ""
            # job_event_messsage += colored("CrowdAI.Job.Event", "cyan", attrs=['bold'])+":  "
            # job_event_messsage += "job_id = " + colored(job_id, "yellow", attrs=['bold'])
            #
            # self.write_above_single_progress_bar(job_event_messsage)
            # self.update_single_progress_bar_description(colored(job_id, 'green', attrs=['bold']))
        elif job_state == JobStates.RUNNING :
            job_event_messsage = ""
            job_event_messsage += colored("CrowdAI.Job.Event", "cyan", attrs=['bold'])+":  "
            job_event_messsage += colored("JOB_RUNNING", "blue", attrs=['bold'])

            self.write_above_single_progress_bar(job_event_messsage)
            self.update_single_progress_bar_description(colored(job_id, 'green', attrs=['bold']))
        elif job_state == JobStates.PROGRESS_UPDATE :
            self.update_single_progress_bar(payload["data"]["percent_complete"])
            self.update_single_progress_bar_description(colored(job_id, 'green', attrs=['bold']))
        elif job_state == JobStates.COMPLETE :
            self.update_single_progress_bar(100)
            job_event_messsage = ""
            job_event_messsage += colored("CrowdAI.Job.Event", "cyan", attrs=['bold'])+":  "
            job_event_messsage += colored("JOB_COMPLETE", "green", attrs=['bold'])

            self.write_above_single_progress_bar(job_event_messsage)
            self.update_single_progress_bar_description(colored(job_id, 'green', attrs=['bold']))
        elif job_state == JobStates.INFO:
            job_event_messsage = ""
            job_event_messsage += colored("CrowdAI.Job.Event", "cyan", attrs=['bold'])+":  "
            job_event_messsage += colored("JOB_INFO", "yellow", attrs=['bold']) +" "+payload["message"]
            self.write_above_single_progress_bar(job_event_messsage)
        elif job_state == JobStates.TIMEOUT:
            job_event_messsage = ""
            job_event_messsage += colored("CrowdAI.Job.Event", "cyan", attrs=['bold'])+":  "
            job_event_messsage += colored("JOB_INFO", "red", attrs=['bold']) +" "+payload["message"]
            self.write_above_single_progress_bar(job_event_messsage)
        else:
            job_event_messsage = ""
            job_event_messsage += colored("CrowdAI.Job.Event", "cyan", attrs=['bold'])+":  "
            job_event_messsage += colored("JOB_ERROR", "red", attrs=['bold'])
            self.write_above_single_progress_bar(job_event_messsage)
            raise CrowdAIExecuteFunctionError("Malformed response from server. \
                                            Please contact the server admins.\n")

    def on_execute_function_response_complete(self, args):
        """
            Placeholder function to be able to account for
            Timeout thresholds
        """
        self.pbar = self.close_single_progress_bar()
        return {}

    def execute_function(self, function_name, data, dry_run=False):
        #TO-DO : Validate if authenticated
        self.response_channel = self.challenge_id+"::"+str(uuid.uuid4())
        #Prepare for response

        # Instantiate Progressbar
        self.instantiate_single_progressbar()

        #NOTE: response_channel is prepended with the session_key to discourage hijacking attempts
        #print "Listening on : ", self.session_key+"::"+self.response_channel
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

        self.socketio.wait_for_callbacks(seconds=self.config['challenges'][self.challenge_id]["TIMEOUT_EXECUTION"])
        #if self.execute_function_response == None:
        #    raise CrowdAIExecuteFunctionError("Evaluation Request Timeout")
        #    # print "Evaluation Request Timed Out..."
        #else:
        #    response = self.execute_function_response
        #    return response["response"]

    def instantiate_single_progressbar(self):
        self.pbar = tqdm(total=100, dynamic_ncols=True, unit="% ", \
                         bar_format="{desc}{percentage:3.0f}% "\
                         "|{bar}|" \
                        #  "{n_fmt}/{total_fmt}" \
                         "[{elapsed}<{remaining}] "\
                         " {rate_fmt}] "\
                         ""\
                         )
        self.last_reported_progress = 0

    def close_single_progress_bar(self):
        self.pbar.close()
        self.last_reported_progress = 0

    def update_single_progress_bar(self, percent_complete):
        if percent_complete > self.last_reported_progress:
            update_length = int(percent_complete)- self.last_reported_progress
            self.pbar.update(update_length)
            self.last_reported_progress += update_length

    def write_above_single_progress_bar(self, line):
        tqdm.write(line)

    def update_single_progress_bar_description(self, line):
        self.pbar.set_description(line)
