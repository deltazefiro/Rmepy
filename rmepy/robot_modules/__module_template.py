import traceback
from .. import logger
from ..decorators import retry

class RobotModuleTemplate(object):
    def __init__(self, robot):
        self._send_msg = robot.send_msg
        self._send_cmd = robot.connection.send_cmd
        self._send_query = robot.connection.send_query
        self._log = logger.Logger(self)

    def _process_response(self, data, type_list):
        try:
            data = data.split(' ')
            if isinstance(type_list, (list, tuple)):
                data = [f(i) if f != bool else bool(int(i))
                        for i, f in zip(data, type_list)]
            else:
                data = [type_list(i) if type_list != bool else bool(int(i))
                        for i in data]
        except (TypeError, ValueError) as e:
            self._log.error(
                "%s: Error at processing response: %s does not match %s" % (traceback.extract_stack()[-2][2], data, type_list))
            data = None
        return data