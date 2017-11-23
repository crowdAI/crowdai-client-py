from __future__ import print_function

import json
import time
import uuid

import logging_helpers as lh
import pkg_resources
from socketIO_client import SocketIO, LoggingNamespace
from termcolor import colored
from tqdm import tqdm

from .crowdai_errors import *
from .events import CrowdAIEvents


class BaseChallenge(object):
    def __init__(self, challenge_id, api_key, config):
        self.api_key = str(api_key).strip()
        self.challenge_id = challenge_id
        self.config = config
        self.session_key = None
        self.latest_response = False
        self.pbar = None
        self.PROGRESS_BAR=True
        self.AGGREGATED_PROGRESS_BAR=False
        self.SUPPRESS_LOGGING_HELPERS=False

    def on_connect(self):
        if not self.SUPPRESS_LOGGING_HELPERS: print(lh.success(CrowdAIEvents.Connection["CONNECTED"], ""))
    def on_disconnect(self):
        if not self.SUPPRESS_LOGGING_HELPERS: print(lh.error(CrowdAIEvents.Connection["DISCONNECTED"], ""))
    def on_reconnect(self):
        if not self.SUPPRESS_LOGGING_HELPERS: print(lh.success(CrowdAIEvents.Connection["RECONNECTED"], ""))

    def _connect(self):
        # TO-DO : Handle socketio connection and disconnection events
        self.socketio = SocketIO(self.config['remote_host'], self.config['remote_port'], LoggingNamespace)
        self.socketio.on('connect', self.on_connect)
        self.socketio.on('disconnect', self.on_disconnect)
        self.socketio.on('reconnect', self.on_reconnect)

    def disconnect(self):
        self.socketio.disconnect()

    def _authenticate_response(self, args):
        if args["response_type"] == CrowdAIEvents.Authentication["SUCCESS"]:
            self.session_key = args["session_token"]
            if not self.SUPPRESS_LOGGING_HELPERS: print(lh.success(CrowdAIEvents.Authentication["SUCCESS"], "Authentication Successful"))
        else:
            # TO-DO: Log authentication error
            if not self.SUPPRESS_LOGGING_HELPERS:
                print(lh.error(CrowdAIEvents.Authentication["ERROR"], args["message"]))
            self.disconnect()
            raise CrowdAIAuthenticationError(args["message"])

    def _authenticate_response_placeholder(self, args):
        pass

    def _authenticate(self):
        if not self.SUPPRESS_LOGGING_HELPERS: print(lh.info(CrowdAIEvents.Authentication[""],
                        "Authenticating for challenge = "+colored(self.challenge_id, "blue", attrs=['bold', 'underline'])))

        self.session_key = None
        self.socketio.on('authenticate_response', self._authenticate_response)
        self.socketio.emit('authenticate', {"API_KEY":self.api_key,
                                           "challenge_id": self.challenge_id,
                                           "client_version":pkg_resources.get_distribution("crowdai").version},
                                           self._authenticate_response_placeholder)
        self.socketio.wait_for_callbacks(seconds=self.config['TIMEOUT_AUTHENTICATE'])
        if self.session_key == None:
            # TO-DO: Log authentication error
            self.disconnect()
            raise CrowdAIAuthenticationError("Authentication Timeout")

    def on_execute_function_response(self, channel_name, payload={}):
        if payload == {}:# TODO: Critical This is a hacky fix. We need to find the exact reason why post-submit events are not in this format.
            payload = channel_name

        payload = json.loads(payload)
        job_state = payload['response_type']
        job_id = payload['job_id']
        sequence_no = payload["data_sequence_no"] #Sequence No being the index of the corresponding input data point in the parallel execution array
        message = payload["message"]
        if job_state == CrowdAIEvents.Job["ERROR"]:
            self.disconnect()
            raise CrowdAIExecuteFunctionError(payload["message"])
        elif job_state == CrowdAIEvents.Job["ENQUEUED"]:
            job_event_messsage = lh.info_yellow(job_state, job_id);
            if self.PROGRESS_BAR:
                self.write_above_single_progress_bar(sequence_no, job_event_messsage)
        elif job_state == CrowdAIEvents.Job["RUNNING"]:
            job_event_messsage = lh.info_blue(job_state, job_id)
            if self.PROGRESS_BAR:
                self.write_above_single_progress_bar(sequence_no, job_event_messsage)
                if not self.AGGREGATED_PROGRESS_BAR:
                    self.update_single_progress_bar_description(sequence_no, colored(job_id, 'green', attrs=['bold']))
        elif job_state == CrowdAIEvents.Job["PROGRESS_UPDATE"]:
            self.update_progress_tracker(sequence_no, payload["data"]["percent_complete"])
            if self.PROGRESS_BAR:
                if not self.AGGREGATED_PROGRESS_BAR:
                    self.update_single_progress_bar_description(sequence_no, colored(job_id, 'green', attrs=['bold']))
        elif job_state == CrowdAIEvents.Job["COMPLETE"]:
            self.update_progress_tracker(sequence_no, 100)
            job_event_messsage = lh.success(job_state, job_id)
            safe_job_event_messsage = job_event_messsage
            # When sequence number is less than 0, it is a JOB_COMPLETE event which is not associated with any
            # current jobs
            if sequence_no >= 0:
                safe_job_event_messsage = job_event_messsage + "\t OK"
                job_event_messsage += u"\t   \U0001F37A "
            else:
                safe_job_event_messsage = job_event_messsage + "\t OK"
                job_event_messsage += u"\t   \U0001F37A \U0001F37A \U0001F37A"

            if self.PROGRESS_BAR:
                try:
                    self.write_above_single_progress_bar(sequence_no, job_event_messsage)
                except UnicodeEncodeError:
                    # If the client doesnt have the relevant codecs for rendering this,
                    # Then dont make a whole mess about it, and instead print the safe_job_event_messsage.
                    self.write_above_single_progress_bar(sequence_no, safe_job_event_messsage)
                if not self.AGGREGATED_PROGRESS_BAR:
                    self.update_single_progress_bar_description(sequence_no, colored(job_id, 'green', attrs=['bold']))
        elif job_state == CrowdAIEvents.Job["INFO"]:
            job_event_messsage = lh.info(job_state, "("+job_id+") "+payload["message"])
            if self.PROGRESS_BAR:
                self.write_above_single_progress_bar(sequence_no, job_event_messsage)
        elif job_state == CrowdAIEvents.Job["TIMEOUT"]:
            job_event_messsage = lh.error(job_state, "("+job_id+") "+payload["message"])
            if self.PROGRESS_BAR:
                self.write_above_single_progress_bar(sequence_no, job_event_messsage)
        else:
            job_event_messsage = lh.error(job_state, "("+job_id+") "+str(payload["message"]))
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

        self._aggregated_responses = []
        for _val in args:
            _item = _val['data']
            _item['job_state'] = _val['response_type']
            _item['message'] = _val['message']
            self._aggregated_responses.append(_item)
        self.aggregated_responses = self._aggregated_responses
        return {}

    def execute_function(self, function_name, data, dry_run=False, parallel=False):
        #TO-DO : Validate if authenticated
        self.response_channel = self.challenge_id+"::"+str(uuid.uuid4())
        #Prepare for response
        self.aggregated_responses = False

        self.instantiate_progress_bars(len(data))

        self.socketio.on(self.response_channel, self.on_execute_function_response)
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

    def instantiate_progress_trackers(self, number):
        if self.SUPPRESS_LOGGING_HELPERS:
            return
        self.last_reported_progress = []
        for k in range(number):
            self.last_reported_progress.append(0)
        self.last_reported_mean_progress = 0

    def update_progress_tracker(self, seq_no, value):
        if self.SUPPRESS_LOGGING_HELPERS:
            return
        diff = 0
        if value > self.last_reported_progress[seq_no]:
            diff = value - self.last_reported_progress[seq_no]
            self.last_reported_progress[seq_no] = value

        if self.PROGRESS_BAR:
            if self.AGGREGATED_PROGRESS_BAR:
                _mean = sum(self.last_reported_progress)*1.0/len(self.last_reported_progress)
                if _mean > self.last_reported_mean_progress:
                    diff = _mean - self.last_reported_mean_progress
                    self.last_reported_mean_progress = _mean
                self.update_single_progress_bar(0, diff)
            else:
                self.update_single_progress_bar(seq_no, diff)

    def instantiate_progress_bars(self, number):
        if self.SUPPRESS_LOGGING_HELPERS:
            return
        self.instantiate_progress_trackers(number)

        if self.PROGRESS_BAR:
            """
                Instantiate only of Progress Bars are enabled
            """
            if self.AGGREGATED_PROGRESS_BAR:
                """
                    Force set numnber of progress bars to 1
                    if AGGREGATED_PROGRESS_BAR is enabled
                """
                number = 1
        else:
            return

        self.pbar = []
        for k in range(number):
            self.pbar.append(tqdm(total=100, dynamic_ncols=True, unit="% ", \
                             bar_format="{desc}{percentage:3.0f}% "\
                             "|{bar}|" \
                            #  "{n_fmt}/{total_fmt}" \
                             "[{elapsed}<{remaining}] "\
                             " {rate_fmt}] "\
                             ""\
                             ))

    def close_all_progress_bars(self):
        if self.SUPPRESS_LOGGING_HELPERS:
            return
        for _idx, _pbar in enumerate(self.pbar):
            _pbar.close()

    def update_single_progress_bar(self, seq_no, diff):
        if self.SUPPRESS_LOGGING_HELPERS:
            return
        try:
            if seq_no != -1:
                foo = self.last_reported_progress[seq_no]
        except Exception:
            return
        self.pbar[seq_no].update(diff)

    def write_above_single_progress_bar(self, seq_no, line):
        if self.SUPPRESS_LOGGING_HELPERS:
            return
        tqdm.write(line)

    def update_single_progress_bar_description(self, seq_no, line):
        if self.SUPPRESS_LOGGING_HELPERS:
            return
        try:
            if seq_no != -1:
                foo = self.last_reported_progress[seq_no]
        except Exception:
            return
        self.pbar[seq_no].set_description(line)

    def verbose(self, v):
        self.SUPPRESS_LOGGING_HELPERS = not v
