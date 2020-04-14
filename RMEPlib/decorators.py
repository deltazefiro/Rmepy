import time
from functools import wraps


def retry(n_retries):
    # A decorator for retrying.
    
    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):
            retry = 0
            while retry < n_retries:
                temp = func(*args, **kwargs)

                if type(temp) == list or type(temp) == tuple:
                    succ, response = temp
                else:
                    succ, response = temp, None

                if succ:
                    return response
                retry += 1
                time.sleep(args[0].retry_interval)
                args[0].log.warn("Retrying %d ..." % retry)
            args[0].log.error("Failed to retry.")
            return None

        return wrapper
    return decorator
