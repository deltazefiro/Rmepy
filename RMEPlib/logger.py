def _get_class_name(who):
    if not who:
        return ""
    elif who.__class__.__name__ == "str":
        return '[' + who + ']'
    else:
        return '[' + who.__class__.__name__ + ']'


def info(msg, where=None):
    """Print infos.

    Args:
        msg: (str) 输出的info信息
        where: (class / object) 用于定位info产生的class

    Returns:
        None
    """
    class_name = _get_class_name(where)
    print("\033[36m" + "[Info]%s: %s" % (class_name, msg) + "\033[0m")


def warn(msg, where=None):
    """Print warnings.

    Args:
        msg: (str) 输出的警告信息
        where: (class / object) 用于定位warning产生的class

    Returns:
        None
    """
    class_name = _get_class_name(where)
    print("\033[33m" + "[Warning]%s %s" % (class_name, msg) + "\033[0m")


def error(msg, where=None):
    """Print warnings.

    Args:
        msg: (str) 输出的错误信息
        where: (class / object) 用于定位error产生的class

    Returns:
        None
    """
    class_name = _get_class_name(where)
    print("=============================================")
    print("\033[31m" + "[Error]%s %s" % (class_name, msg) + "\033[0m")
    temp = input("Force to continue? (y/n) ")
    print("=============================================")
    if temp.upper() != 'Y':
        exit()
