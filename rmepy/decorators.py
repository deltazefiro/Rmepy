import time
import functools
from inspect import signature
from . import logger


def retry(n_retries=3, retry_interval=1):
    # A decorator for retrying.

    def decorator(func):

        @functools.wraps(func)
        def new_func(*args, **kwargs):

            log = __get_logger(args, 'Retry')

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
                time.sleep(retry_interval)
                log.warn("Retrying %d ..." % retry)
            log.error("Failed to retry.")
            return None
        return new_func

    return decorator


# def accepts(**expectations):
#     """对输入变量进行类型检测和范围检查

#     Inspired by  http://code.activestate.com/recipes/578809-decorator-to-check-method-param-types/

#     Example:
#         @accepts(arg1=(int, 0, 20), arg2=(float, 0.0, 30.0))
#         def func(arg1, arg2):
#             pass

#     todo: float 与 int 的自动转换

#     """

#     def decorator(func):
#         func_code = func.__code__
#         func_name = func.__name__

#         @functools.wraps(func)
#         def new_func(*args, **kwargs):
#             if func_code.co_varnames[0] == 'self' and args[0].log == logger.Logger:
#                 log = args[0].log
#             else:
#                 log = logger.Logger('Accept check')

#             for idx, val in enumerate(args):
#                 if func_code.co_varnames[idx] in expectations:
#                     expectation = expectations[func_code.co_varnames[idx]]

#                     if type(expectation) == type:
#                         if not isinstance(val, expectation):
#                             log.error("%s: arg '%s'=%r does not match %s" % (
#                                 func_name, func_code.co_varnames[idx], val, expectation))

#                     elif not (isinstance(val, expectation[0]) and expectation[1] <= val <= expectation[2]):
#                         log.error("%s: arg '%s' expects %s from %s to %s, but got %r" % (
#                             func_name, func_code.co_varnames[idx], expectation[0], expectation[1], expectation[2], val))

#             for key, val in kwargs.items():
#                 # if key in expectations and not isinstance(val, expectations[key]):
#                 #     log.error("arg '%s'=%r does not match %s" %
#                 #               (key, val, expectations[key]))
#                 if key in expectations:
#                     expectation = expectations[key]

#                     if type(expectation) == type:
#                         if not isinstance(val, expectation):
#                             log.error("%s: Arg '%s'=%r does not match %s" % (
#                                 func_name, key, val, expectation))

#                     elif not (isinstance(val, expectation[0]) and expectation[1] <= val <= expectation[2]):
#                         log.error("%s: Arg '%s' expects %s from %s to %s, but got %r" % (
#                             func_name, key, expectation[0], expectation[1], expectation[2], val))

#             return func(*args, **kwargs)

#         new_func.__name__ = func_name
#         return new_func

#     return decorator


def accepts(*expc_args, **expc_kwargs):
    """对输入变量进行类型检测和范围检查

     Inspired by  https://python3-cookbook.readthedocs.io/zh_CN/latest/c09/p07_enforcing_type_check_on_function_using_decorator.html

     Example:
         @accepts((int, 0, 20), arg2=(float, 0.0, 30.0))
         def func(arg1, arg2):
             pass

     """
    def decorate(func):

        @functools.wraps(func)
        def wrapper(*args, **kwargs):

            sig = signature(func)
            log = __get_logger(args, 'Acceptable check')
            func_name = func.__name__

            if func.__code__.co_varnames[0] == 'self':
                is_func_in_class = True
                bound_expc = sig.bind_partial(None, *expc_args, **expc_kwargs).arguments
            else:
                is_func_in_class = False
                bound_expc = sig.bind_partial(*expc_args, **expc_kwargs).arguments

            bound_values = sig.bind(*args, **kwargs).arguments
            
            for key, value in bound_values.items():
                if key in bound_expc and key != 'self':

                    expectation = bound_expc[key]

                    if type(expectation) == type:
                        bound_values[key] = __type_transform(value, expectation)
                        if bound_values[key] == None:
                            log.error("%s: Arguments '%s' expects %s, but got %r" % (
                                func_name, key, expectation, value))

                    else:
                        bound_values[key] = __type_transform(value, expectation[0])
                        if bound_values[key] == None or not expectation[1] <= value <= expectation[2]:
                            log.error("%s: Arguments '%s' expects %s from %s to %s, but got %r" % (
                                func_name, key, expectation[0], expectation[1], expectation[2], value))

            return func(**bound_values)
        return wrapper
    return decorate

def __type_transform(value, expc_type):
    if expc_type == bool and type(value) == int:
        return int(value) # True/False -> 1/0
    if isinstance(value, expc_type):
        return value
    elif expc_type == float and type(value) == int:
        return float(value)
    elif expc_type == str:
        return str(value)
    else:
        return None

def __get_logger(args, alternative_name):
    try:
        if type(args[0].log) == logger.Logger:
            return args[0].log
    except Exception:
        pass

    try:
        if type(args[0]._log) == logger.Logger:
            return args[0]._log
    except Exception:
        pass

    return logger.Logger(alternative_name)