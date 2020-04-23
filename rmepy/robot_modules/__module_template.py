from .. import logger

class RobotModuleTemplate(object):
    def __init__(self, robot):
        self.send_cmd = robot.send_cmd
        self.send_query = robot.send_query
        self.log = logger.Logger('Commends')

    def _process_response(self, data, type_list):
        try:
            data = data.split(' ')
            if type(type_list) == list:
                data = [f(i) if f != bool else bool(int(i))
                        for i, f in zip(data, type_list)]
            else:
                data = [type_list(i) if type_list != bool else bool(int(i))
                        for i in data]
        except (TypeError, ValueError) as e:
            self.log.error(
                "Error at processing response: %s does not match %s" % (data, type_list))
            data = None
        return data