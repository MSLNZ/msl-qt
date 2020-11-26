import time
import logging
from functools import wraps

logger = logging.getLogger(__name__)


class ContextDecorator(object):

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

    def __enter__(self):
        # Note: Returning self means that in "with ... as x", x will be self
        return self

    def __exit__(self, typ, val, traceback):
        pass

    def __call__(self, f):
        self.function_name = f.__qualname__

        @wraps(f)
        def wrapper(*args, **kw):
            with self:
                return f(*args, **kw)

        return wrapper


class Profile(ContextDecorator):

    def __enter__(self):
        self.t0 = time.perf_counter()
        return self

    def __exit__(self, typ, val, traceback):
        logger.debug(self.function_name + ': {:.3f} seconds'.format(time.perf_counter()-self.t0))
