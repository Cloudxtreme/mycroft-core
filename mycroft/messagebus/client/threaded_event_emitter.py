from pyee import EventEmitter
from multiprocessing.pool import ThreadPool


class ThreadedEventEmitter(EventEmitter):
    """ Event Emitter using the threadpool to run event functions in
        separate threads using a threadpool.
    """
    def __init__(self, threads=None):
        super().__init__()
        self.pool = ThreadPool(threads or 10)

    def emit(self, event, *args, **kwargs):
        """ Override the normal emit launching the function using
            threadpool.
        """
        for f in self._events[event]:
            self.pool.apply_async(f, args, kwargs)
        return True
