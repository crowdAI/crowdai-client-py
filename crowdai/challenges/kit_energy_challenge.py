from .base_challenge import BaseChallenge
import logging_helpers as lh
from .events import CrowdAIEvents
from .crowdai_errors import CrowdAIAPINotAvailableError
import requests
from .upload_helpers import upload_in_chunks, IterableToFileAdapter


class KITEnergyChallenge(BaseChallenge):
    def __init__(self, api_key, config):
        self.challenge_id = "KITEnergyChallenge"
        super(
            KITEnergyChallenge,
            self).__init__(self.challenge_id, api_key, config)
        self._connect()
        self._authenticate()

    def _obtain_presigned_url(self, dry_run=False):
        url = self.config['crowdai_remote_api']
        url += "{}/presign".format(self.api_key)

        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            raise CrowdAIAPINotAvailableError(
                    "Unable to connect to CrowdAI API."
                    )

    def submit(self, filename):
        print(
            lh.blue(
                CrowdAIEvents.Misc["FILE_UPLOAD"] +
                " : Preparing for file upload"))
        # Validate that the file is indeed a valid gzip file
        response = self._obtain_presigned_url()

        print(lh.blue(CrowdAIEvents.Misc["FILE_UPLOAD"]+" : Uploading file"))
        url = response["presigned_url"]
        file_key = response["s3_key"]

        # Instantiate Progress Trackers
        self.instantiate_progress_bars(1)
        requests.put(
            url,
            data=IterableToFileAdapter(
                upload_in_chunks(filename, self, chunksize=5000)
                )
            )
        self.close_all_progress_bars()

        result = self.execute_function(
                "grade_submission",
                [{"file_key": file_key}]
                )[0]
        del result["job_state"]
        return result
