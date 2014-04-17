"""
Defines the Environment class which holds all of the per instance values data
for the server.

The per instance values includes all queues, connection lists and server stats.
"""

class Environment(object):
    """
    The Environment class contains class variables that hold all of the queues
    and lists.
    """

    command_queue = None
    input_queue = None

    commands = {
        'global' : None,
        'conn_screen' : None,
        'connected' : None,
    }

    def __init__(self):
        """ Doesn't do anything! """
        pass
