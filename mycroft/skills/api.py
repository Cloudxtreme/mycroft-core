from mycroft.messagebus.message import Message
bus = None


def init_skill_api(mycroft_bus):
    global bus
    bus = mycroft_bus


class SkillApi():
    """ SkillApi class, methods are built from the method_dict provided when
        initializing the skill.
    """
    def __init__(self, method_dict):
        self.method_dict = method_dict
        for key in method_dict:
            def get_method(k):
                def method(**kwargs):
                    m = self.method_dict[k]
                    return bus.wait_for_response(Message(m['type'],
                                                         data=kwargs))
                return method

            self.__setattr__(key, get_method(key))

    @staticmethod
    def get(skill):
        """ Generate api object from skill id.

        Arguments:
            skill (str): skill id for target skill

        Returns:
            SkillApi
        """
        api = bus.wait_for_response(Message('{}.public_api'.format(skill)))
        if api:
            return SkillApi(api.data)
        else:
            return None
