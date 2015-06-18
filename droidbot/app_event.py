# This file is responsible for generating events to interact with app at runtime
# The events includes:
#     1. UI events. click, touch, etc
#     2, intent events. broadcast events of App installed, new SMS, etc.
# The intention of these events is to exploit more mal-behaviours of app as soon as possible
__author__ = 'liyc'
import logging

event_policies = [
    "none",
    "monkey",
    "static",
    "dynamic",
    "file"
]


class AppEvent(object):
    """
    The base class of all events
    """
    # TODO implement this class and its subclasses
    pass


class UIEvent(AppEvent):
    """
    This class describes a UI event of app, such as touch, click, etc
    """
    pass


class ExtendedUIEvent(UIEvent):
    """
    An extended UI event, which knows the UI state on which it is performing
    """
    pass


class IntentEvent(AppEvent):
    """
    An event describing an intent
    """
    pass


class AppEventManager(object):
    """
    This class manages all events to send during app running
    """

    def __init__(self, device, app, event_policy, event_count):
        """
        construct a new AppEventManager instance
        :param device: instance of Device
        :param app: instance of App
        :param event_policy: policy of generating events, string
        :return:
        """
        self.logger = logging.getLogger('AppEventManager')
        self.device = device
        self.app = app
        self.policy = event_policy
        self.events = []
        self.event_factory = None
        self.count = event_count

        if not self.count or self.count == None:
            self.count = 100

        if not self.policy or self.policy == None:
            self.policy = "none"

        if self.policy == "none":
            self.event_factory = None
        elif self.policy == "monkey":
            self.event_factory = DummyEventFactory()
        elif self.policy == "static":
            self.event_factory = StaticEventFactory(app)
        elif self.policy == "dynamic":
            self.event_factory = DynamicEventFactory(app)
        else:
            self.event_factory = FileEventFactory(self.policy)

    def add_event(self, event):
        """
        add one event to the event list
        :param event: the event to be added, should be subclass of AppEvent
        :return:
        """
        self.events.append(event)
        self.device.send_event(event)

    def dump(self, file):
        """
        dump the event information to a file
        :param file: the file path to output the events
        :return:
        """
        # TODO implement this method

    def on_state_update(self, old_state, new_state):
        """
        callback method invoked by AppstateMonitor
        :param old_state: origin state of App
        :param new_state: new state of App
        :return:
        """
        # TODO implement this method

    def set_event_factory(self, event_factory):
        """
        set event factory of the app
        :param event_factory: the factory used to generate events
        :return:
        """
        self.event_factory = event_factory

    def start(self):
        """
        start sending event
        """
        self.logger.info("start sending events, policy is %s" % self.policy)
        if self.event_factory != None:
            self.event_factory.start(self)
        else:
            monkey_cmd = ["monkey", "--throttle", "1000", "-v"]
            if self.app.package_name != None:
                monkey_cmd += ["-p", self.app.package_name]
            monkey_cmd.append(str(self.count))
            self.device.get_adb().shell(" ".join(monkey_cmd))


class EventFactory(object):
    """
    This class is responsible for generating events to stimulate more app behaviour
    It should call AppEventManager.send_event method continuously
    """
    # TODO implement this class and its subclasses
    def start(self, event_manager):
        """
        start producing events
        :param event_manager: instance of AppEventManager
        """
        count = 0
        while count < event_manager.count:
            event = self.generate_event()
            event_manager.add_event(event)

    def generate_event(self):
        """
        generate a event
        """
        raise NotImplementedError

class DummyEventFactory(EventFactory):
    """
    A dummy factory which produces AppEventManager.send_event method in a random manner
    """
    pass


class StaticEventFactory(EventFactory):
    """
    A factory which produces events based on static analysis result
    for example, manifest file and sensitive API it used
    """
    def __init__(self, app):
        """
        create a StaticEventFactory from app analysis result
        :param instance of App
        """
        self.app = app


class DynamicEventFactory(EventFactory):
    """
    A much wiser factory which produces events based on the current app state
    """
    def __init__(self, app):
        """
        create a DynamicEventFactory from app dynamic state
        :param instance of App
        """
        self.app = app


class FileEventFactory(EventFactory):
    """
    factory which produces events from file
    """
    def __init__(self, file):
        """
        create a FileEventFactory from a json file
        :param file path string
        """
        self.file = file