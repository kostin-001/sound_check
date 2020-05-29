from sound_check_app import constants
from sound_check_app import file_utils


class BaseRecognizer(object):

    def __init__(self, sound_check):
        self.sound_check = sound_check
        self.sample_rate = constants.DEFAULT_SAMPLE_RATE

    def _recognize(self, data, top_limit=10):
        return self.sound_check.find_matches(data, top_limit, sr=self.sample_rate)

    def recognize(self, option):
        pass  # base class does nothing


class FileRecognizer(BaseRecognizer):
    def __init__(self, sound_check):
        super(FileRecognizer, self).__init__(sound_check)

    def recognize_file(self, filename, top_limit=10):
        frames, file_hash = file_utils.read_file(filename, self.sound_check.limit)
        return self._recognize(frames, top_limit)

    def recognize(self, filename, top_limit=10):
        return self.recognize_file(filename, top_limit)
