import os


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


class IterableToFileAdapter(object):
    """
    Reference:
    https://stackoverflow.com/questions/13909900/progress-of-python-requests-post
    """
    def __init__(self, iterable):
        self.iterator = iter(iterable)
        self.length = len(iterable)

    def read(self, size=-1):
        # TBD: add buffer for `len(data) > size` case
        return next(self.iterator, b'')

    def __len__(self):
        return self.length
