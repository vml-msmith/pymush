from muse.network.connections import global_connection_handler

class Notifier(object):
    def __init__(self):
        self.exclude_list = []

    def notify(self, object, data):
        if object.type == 'Player':
            self.notify_player_descriptor(object, data)
        # Do other notify type stuff. Trigger things and junk

    def notify_by_protocol(self, object, protocol, data, fallback):
        if object.type == 'Player':
            self.notify_player_descriptor_by_protocol(object, protocol, data, fallback)

        # other stuff always gets fallback behavior
        # Do other notify type stuff. Trigger things and junk

    def exclude(self, object):
        self.exclude_list.append(object)

        return self

    def notify_surroundings(self, object, data):
        # Build a list of surroundings.

        list = []
        loc = object.location
        if loc != None:
            list.append(loc)
            contents = loc.contents
            if contents != None:
                for v in contents:
                    list.append(v)

        print list

        for v in [v for v in list if v not in self.exclude_list]:
            print v
            self.notify(v, data)

    def notify_player_descriptor(self, object, message):
        # Try and notify sockets too!
        global_connection_handler.tell_dbref(object.ref, message)

    def notify_player_descriptor_by_protocol(self, object, protocol, data, fallback):
        global_connection_handler.tell_dbref_protocol(object.ref, protocol, data, fallback)
