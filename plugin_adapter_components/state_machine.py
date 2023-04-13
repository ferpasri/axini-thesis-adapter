"""
A class to encapsulate the plugin adapter state machine from the adapter core.
"""
class StateMachine:
    def __init__(self):
        self.state = "disconnected"


    """ Check if the statemachine is in the disconnected state """
    def is_disconnected(self):
        return self.state == "disconnected"


    """ Set the statemachine in the disconnected state """
    def set_disconnect(self):
        self.state = "disconnected"

    """ Check if the statemachine is in the connected state """
    def is_connected(self):
        return self.state == "connected"


    """ Set the statemachine in the connected state """
    def set_connected(self):
        self.state = "connected"


    """ Check if the statemachine is in the announced state """
    def is_announced(self):
        return self.state == "announced"


    """ Set the statemachine in the announced state """
    def set_announced(self):
        self.state = "announced"


    """ Check if the statemachine is in the configured state """
    def is_configured(self):
        return self.state == "configured"


    """ Set the statemachine in the configured state """
    def set_configured(self):
        self.state = "configured"


    """ Check if the statemachine is in the ready state """
    def is_ready(self):
        return self.state == "ready"


    """ Set the statemachine in the ready state """
    def set_ready(self):
        self.state = "ready"


    """ Check if the statemachine is in the error state """
    def is_error(self):
        return self.state == "error"


    """ Set the statemachine in the error state """
    def set_error(self):
        self.state = "error"
