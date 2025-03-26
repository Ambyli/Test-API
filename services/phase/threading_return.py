import threading
import functools
import time
from threading import Thread


# allows a thread to return a value
# this behavior is not a default function of python's threading
class ThreadWithReturnValue(Thread):
    def __init__(
        self, group=None, target=None, name=None, args=(), kwargs={}, Verbose=None
    ):
        Thread.__init__(self, group, target, name, args, kwargs)
        # define return object
        self._return = None
        # create thread checker object
        self._done = False

    # runs target and gets return
    def run(self):
        # update done status
        self._done = False
        if self._target is not None:
            # invoke function target
            self._return = self._target(*self._args, **self._kwargs)
            # upadte done status
            self._done = True

    # joins thread
    def join(self, *args):
        # join thread
        Thread.join(self, *args)
        # return result from target
        return self._return

    # returns done status
    def done(self):
        return self._done

    def stop(self):
        exit()


def synchronize(function):
    lock = threading.Lock()

    @functools.wraps(function)
    def wrapper(self, *args, **kwargs):
        with lock:
            return function(self, *args, **kwargs)

    return wrapper


def main():
    thread = ThreadWithReturnValue(target=lambda: time.sleep(10))
    thread.start()
    breaker = 0
    while thread.done() is False and breaker < 5000:
        print(thread.done())
        breaker += 1

    thread.join()
    print(thread.done())


if __name__ == "__main__":
    main()
