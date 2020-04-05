def _get_class_name(who):
    if not who:
        return ""
    elif who.__class__.__name__ == "str":
        return '[' + who + ']'
    else:
        return '[' + who.__class__.__name__ + ']'


def info(msg, who=None):
    class_name = _get_class_name(who)
    print("\033[36m" + "[Info]%s: %s" % (class_name, msg) + "\033[0m")


def warn(msg, who=None):
    """Print warnings.

    To replace warnings.warn() whose output is too complex.
    用于替代输出复杂的 wanrnings.warn()

    Args:
        msg: (str) 输出的错误信息
        who: (class / object) 用于定位warning产生的class

    Returns:
        None
    """
    class_name = _get_class_name(who)
    print("\033[33m" + "[Warning]%s %s" % (class_name, msg) + "\033[0m")
