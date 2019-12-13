import contextlib

from rest_registration.verification import get_current_timestamp


@contextlib.contextmanager
def capture_time(current_timestamp_getter=get_current_timestamp):
    timer = Timer(current_timestamp_getter=current_timestamp_getter)
    timer.set_start_time()
    try:
        yield timer
    finally:
        timer.set_end_time()


class Timer:

    def __init__(self, current_timestamp_getter=get_current_timestamp):
        super().__init__()
        self._get_current_timestamp = current_timestamp_getter
        self._start_time = None
        self._end_time = None

    @property
    def start_time(self):
        assert self._start_time is not None, "start_time was not set"
        return self._start_time

    @start_time.setter
    def start_time(self, value):
        assert self._start_time is None, "start_time is already set"
        self._start_time = value

    @property
    def end_time(self):
        assert self._end_time is not None, "end_time was not set"
        return self._end_time

    @end_time.setter
    def end_time(self, value):
        assert self._end_time is None, "end_time is already set"
        self._end_time = value

    def set_start_time(self):
        self.start_time = self._get_current_timestamp()

    def set_end_time(self):
        self.end_time = self._get_current_timestamp()
