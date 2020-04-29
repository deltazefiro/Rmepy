import traceback

# 是否输出 debuginfo 信息
DEBUG = True

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
        print("\033[0;36m" + "[Info][%s]%s: %s" % (self.name, traceback.extract_stack()[-2][2], msg) + "\033[0m")

    def warn(self, msg):
        """Print warnings.

        Args:
            msg: (str) 输出的警告信息

        Returns:
            None
        """
        print("\033[33m" + "[Warning][%s]%s: %s" % (self.name, traceback.extract_stack()[-2][2], msg) + "\033[0m")

    def error(self, msg):
        """Print errors.

        输出错误并提供traceback或者强制继续

        Args:
            msg: (str) 输出的错误信息

        Returns:
            None
        """
        print("=============================================")
        print("\033[0;31m" + "[Error][%s]%s: %s" % (self.name, traceback.extract_stack()[-2][2], msg) + "\033[0m")
        temp = input("Force to continue? ('y' to continue / 'n' to print Traceback) ")
        print("=============================================")
        if temp.upper() != 'Y':
            print("\n\033[0;31m" + "Traceback (most recent call last):" + "\033[0m")
            for line in traceback.format_stack()[:-1]:
                print("\033[31m" + line  + "\033[0m")
            print("\n=============================================")
            exit()
    
    def debuginfo(self, msg):
        """Print debug msg.

        Args:
            msg: (str) 输出的调试信息

        Returns:
            None
        """
        if DEBUG:
            print("\033[2m" + "[Debug]%s: %s" % (self.name, msg) + "\033[0m")

    def debug(self, msg):
        """Print highlighted debug msg.

        Args:
            msg: (str) 输出的调试信息

        Returns:
            None
        """
        print("\033[7m" + "[Debug]%s: %s" % (self.name, msg) + "\033[0m")



if  __name__ == '__main__':
    log = Logger('test')

    log.info('test')
    log.warn('test')
    log.debuginfo('test')
    log.debug('test')

    print('aaaa')
    log.error('test')