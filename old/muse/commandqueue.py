import Queue

class CommandQueueObject(object):
    def __init__(self, object, command):
        self.object = object
        self.command = command

global_command_queue = Queue.Queue()
