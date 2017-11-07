from .base_challenge import BaseChallenge
import logging_helpers as lh
from .events import CrowdAIEvents
from .crowdai_errors import *
import requests
import time
import os
import sys
import tarfile

class Learning2RunChallengeNIPS2017(BaseChallenge):
    def __init__(self, api_key, config):
        self.challenge_id = "Learning2RunChallengeNIPS2017"
        super(Learning2RunChallengeNIPS2017, self).__init__(self.challenge_id, api_key, config)
        self._connect()
        self._authenticate()

    def _obtain_presigned_url(self, dry_run=False):
        url = self.config['crowdai_remote_api'] + "{}/presign".format(self.api_key)
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            # TODO: Wrap it in a correct CrowdAIException Class
            raise CrowdAIAPINotAvailableError("Unable to connect to CrowdAI API.")

    def submit(self, filename):
        print(lh.blue(CrowdAIEvents.Misc["FILE_UPLOAD"]+" : Preparing for file upload"))
        # Validate that the file is indeed a valid gzip file
        if not tarfile.is_tarfile(filename):
            err_message = "`{}` doesnot seem to be a valid tar file. The grader accepts only valid tar dumps of docker containers.".format(filename)
            raise Exception(err_message)

        response = self._obtain_presigned_url()

        print(lh.blue(CrowdAIEvents.Misc["FILE_UPLOAD"]+" : Uploading file"))
        url = response["presigned_url"]
        file_key = response["s3_key"]

        #Instantiate Progress Trackers
        self.instantiate_progress_bars(1)
        r = requests.put(url, data=IterableToFileAdapter(upload_in_chunks(filename, self, chunksize=5000)))
        self.close_all_progress_bars()

        result = self.execute_function("grade_submission", [{"file_key":file_key}])[0]
        del result["job_state"]
        return result

class upload_in_chunks(object):
    def __init__(self, filename, challenge_instance, chunksize=1 << 13):
        self.filename = filename
        self.chunksize = chunksize
        self.totalsize = os.path.getsize(filename)
        self.challenge_instance = challenge_instance
        self.readsofar = 0

    def __iter__(self):
        with open(self.filename, 'rb') as file:
            while True:
                data = file.read(self.chunksize)
                if not data:
                    break
                self.readsofar += len(data)
                percent = self.readsofar * 1e2 / self.totalsize
                if percent >= 0 and percent <= 100:
                    self.challenge_instance.update_progress_tracker(0, percent)
                yield data

    def __len__(self):
        return self.totalsize

#TODO: Refactor
class IterableToFileAdapter(object):
    """
        Reference: https://stackoverflow.com/questions/13909900/progress-of-python-requests-post
    """
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.length = len(iterable)

    def read(self, size=-1): # TBD: add buffer for `len(data) > size` case
        return next(self.iterator, b'')

    def __len__(self):
        return self.length
