
class Logger():
    def __init__(self, name):
        if name.__class__.__name__ == 'str':
            self.name = name
        else:
            self.name = name.__class__.__name__

    def info(self, msg):
        """Print infos.

        Args:
            msg: (str) 输出的info信息

        Returns:
            None
        """
        print("\033[0;36m" + "[Info]%s: %s" % (self.name, msg) + "\033[0m")


    def warn(self, msg):
        """Print warnings.

        Args:
            msg: (str) 输出的警告信息

        Returns:
            None
        """
        print("\033[0;33m" + "[Warning]%s: %s" % (self.name, msg) + "\033[0m")


    def error(self, msg):
        """Print errors.

        Args:
            msg: (str) 输出的错误信息

        Returns:
            None
        """
        print("=============================================")
        print("\033[0;31m" + "[Error]%s: %s" % (self.name, msg) + "\033[0m")
        temp = input("Force to continue? ('y' to continue / 'n' to print Traceback) ")
        print("=============================================")
        if temp.upper() != 'Y':
            print("\033[0;31m", end='')
            raise


if  __name__ == '__main__':
    log = Logger('test')
    log.info('test')
    log.warn('test')
    log.error('test')