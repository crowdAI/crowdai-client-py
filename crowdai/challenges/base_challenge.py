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
        self.api_key = str(api_key).strip()
        self.challenge_id = challenge_id
        self.config = config
        self.session_key = None
        self.latest_response = False
        self.pbar = None
        self.PROGRESS_BAR=True

    def _connect(self):
        # TO-DO : Handle socketio connection and disconnection events
        self.socketio = SocketIO(self.config['remote_host'], self.config['remote_port'], LoggingNamespace)
    def disconnect(self):
        self.socketio.disconnect()

    def _authenticate_response(self, args):
        if args["job_state"] == JobStates.COMPLETE:
            self.session_key = args["session_token"]
            authentication_successful_message = ""
            authentication_successful_message += colored("CrowdAI.Authentication.Event", "cyan", attrs=['bold'])+":  "
            authentication_successful_message += colored("Authentication Successful", "green", attrs=['bold'])
            print authentication_successful_message
        else:
            # TO-DO: Log authentication error
            self.disconnect()
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
            self.disconnect()
            raise CrowdAIAuthenticationError("Authentication Timeout")
        else:
            # session_key_message = ""
            # session_key_message += colored("CrowdAI.Authentication.Event", "blue", attrs=['bold'])+":  "
            # session_key_message += "session_key="+colored(self.session_key, "blue", attrs=['bold'])
            # print session_key_message
            pass
            # Temporarily ignore printing session_key
            # TO-DO: Log authentication successful

    def on_execute_function_response(self, channel_name, payload={}):
        if payload == {}:# TODO: Critical This is a hacky fix. We need to find the exact reason why post-submit events are not in this format.
            payload = channel_name

        payload = json.loads(payload)
        job_state = payload['job_state']
        job_id = payload['job_id']
        sequence_no = payload["data_sequence_no"] #Sequence No being the index of the corresponding input data point in the parallel execution array
        message = payload["message"]

        if job_state == JobStates.ERROR:
            self.disconnect()
            raise CrowdAIExecuteFunctionError(payload["message"])
        elif job_state == JobStates.ENQUEUED :
            job_event_messsage = ""
            job_event_messsage += colored("CrowdAI.Job.Event", "cyan", attrs=['bold'])+":  "
            job_event_messsage += colored("JOB_ENQUEUED ", "yellow", attrs=['bold'])+"("+job_id+") "

            if self.PROGRESS_BAR:
                self.write_above_single_progress_bar(sequence_no, job_event_messsage)

            # job_event_messsage = ""
            # job_event_messsage += colored("CrowdAI.Job.Event", "cyan", attrs=['bold'])+":  "
            # job_event_messsage += "job_id = " + colored(job_id, "yellow", attrs=['bold'])
            #
            # self.write_above_single_progress_bar(sequence_no, job_event_messsage)
            # self.update_single_progress_bar_description(sequence_no, colored(job_id, 'green', attrs=['bold']))
        elif job_state == JobStates.RUNNING :
            job_event_messsage = ""
            job_event_messsage += colored("CrowdAI.Job.Event", "cyan", attrs=['bold'])+":  "
            job_event_messsage += colored("JOB_RUNNING ", "blue", attrs=['bold'])+"("+job_id+") "

            if self.PROGRESS_BAR:
                self.write_above_single_progress_bar(sequence_no, job_event_messsage)
                self.update_single_progress_bar_description(sequence_no, colored(job_id, 'green', attrs=['bold']))
        elif job_state == JobStates.PROGRESS_UPDATE :
            if self.PROGRESS_BAR:
                self.update_single_progress_bar(sequence_no, payload["data"]["percent_complete"])
                self.update_single_progress_bar_description(sequence_no, colored(job_id, 'green', attrs=['bold']))
        elif job_state == JobStates.COMPLETE :
            if self.PROGRESS_BAR:
                self.update_single_progress_bar(sequence_no, 100)
            job_event_messsage = ""
            job_event_messsage += colored("CrowdAI.Job.Event", "cyan", attrs=['bold'])+":  "

            # When sequence number is less than 0, it is a JOB_COMPLETE event which is not associated with any
            # current jobs
            if sequence_no >= 0:
                job_event_messsage += colored("JOB_COMPLETE " , "green", attrs=['bold'])+"("+job_id+") "
                job_event_messsage += u"\t   \U0001F37A "
            else:
                job_event_messsage += colored("JOB_COMPLETE :: "+message+"", "green", attrs=['bold'])
                job_event_messsage += u"\t   \U0001F37A \U0001F37A \U0001F37A"
            if self.PROGRESS_BAR:
                self.write_above_single_progress_bar(sequence_no, job_event_messsage)
                self.update_single_progress_bar_description(sequence_no, colored(job_id, 'green', attrs=['bold']))
        elif job_state == JobStates.INFO:
            job_event_messsage = ""
            job_event_messsage += colored("CrowdAI.Job.Event", "cyan", attrs=['bold'])+":  "
            job_event_messsage += colored("JOB_INFO ("+job_id+") " + payload["message"], "yellow", attrs=['bold'])

            if self.PROGRESS_BAR:
                self.write_above_single_progress_bar(sequence_no, job_event_messsage)
        elif job_state == JobStates.TIMEOUT:
            job_event_messsage = ""
            job_event_messsage += colored("CrowdAI.Job.Event", "cyan", attrs=['bold'])+":  "
            job_event_messsage += colored("JOB_INFO ("+job_id+")", "red", attrs=['bold']) +" "+payload["message"]

            if self.PROGRESS_BAR:
                self.write_above_single_progress_bar(sequence_no, job_event_messsage)
        else:
            job_event_messsage = ""
            job_event_messsage += colored("CrowdAI.Job.Event", "cyan", attrs=['bold'])+":  "
            job_event_messsage += colored("JOB_ERROR ("+job_id+")", "red", attrs=['bold'])

            if self.PROGRESS_BAR:
                self.write_above_single_progress_bar(sequence_no, job_event_messsage)
            raise CrowdAIExecuteFunctionError("Malformed response from server. \
                                            Please update your crowdai package, and if the problem still persists contact the server admins.\n")

    def on_execute_function_response_complete(self, args):
        """
            Placeholder function to be able to account for
            Timeout thresholds
        """
        if self.PROGRESS_BAR:
            self.close_all_progress_bars()

        if args["job_state"] == JobStates.ERROR:
            # TODO: Possible to raise different kinds of errors by matching
            # the beginning of the message to custom string markers
            raise CrowdAIExecuteFunctionError(args["message"])
        if args["job_state"] == JobStates.COMPLETE:
            self.aggregated_responses = args["data"]
        return {}

    def execute_function(self, function_name, data, dry_run=False, parallel=False):
        #TO-DO : Validate if authenticated
        self.response_channel = self.challenge_id+"::"+str(uuid.uuid4())
        #Prepare for response
        self.aggregated_responses = False

        # Instantiate Progressbar
        if self.PROGRESS_BAR:
            number_of_processes = 1
            if parallel:
                number_of_processes = len(data)
            self.instantiate_progress_bars(number_of_processes)

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
                            "dry_run" : dry_run,
                            "parallel" : parallel
                        }, self.on_execute_function_response_complete)

        self.socketio.wait_for_callbacks(seconds=self.config['challenges'][self.challenge_id]["TIMEOUT_EXECUTION"])

        """
        This keeps checking until the aggregated_responses are prepared by the final on_execute_function_response_complete
        and then it returns the same to the calling function
        This is only to ensure that the function is blocking function
        """
        #TODO Explore if we can come up with an event based mechanism for the same
        while True:
            if self.aggregated_responses:
                return self.aggregated_responses
            time.sleep(2)

        #if self.execute_function_response == None:
        #    raise CrowdAIExecuteFunctionError("Evaluation Request Timeout")
        #    # print "Evaluation Request Timed Out..."
        #else:
        #    response = self.execute_function_response
        #    return response["response"]

    def instantiate_progress_bars(self, number):
        self.pbar = []
        self.last_reported_progress = []
        for k in range(number):
            self.pbar.append(tqdm(total=100, dynamic_ncols=True, unit="% ", \
                             bar_format="{desc}{percentage:3.0f}% "\
                             "|{bar}|" \
                            #  "{n_fmt}/{total_fmt}" \
                             "[{elapsed}<{remaining}] "\
                             " {rate_fmt}] "\
                             ""\
                             ))
            self.last_reported_progress.append(0)

    def close_all_progress_bars(self):
        for _idx, _pbar in enumerate(self.pbar):
            _pbar.close()
            self.last_reported_progress[_idx] = 0

    def update_single_progress_bar(self, seq_no, percent_complete):
        try:
            if seq_no != -1:
                foo = self.last_reported_progress[seq_no]
        except:
            return

        if percent_complete > self.last_reported_progress[seq_no]:
            update_length = int(percent_complete)- self.last_reported_progress[seq_no]
            self.pbar[seq_no].update(update_length)
            self.last_reported_progress[seq_no] += update_length

    def write_above_single_progress_bar(self, seq_no, line):
        tqdm.write(line)

    def update_single_progress_bar_description(self, seq_no, line):
        try:
            if seq_no != -1:
                foo = self.last_reported_progress[seq_no]
        except:
            return
        self.pbar[seq_no].set_description(line)
