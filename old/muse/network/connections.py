from muse.environment import Environment
class ConnectionManager(object):
    def __init__(self):
        self.registered_connections = {}

    def register(self, ws):
        if ws.get_id() in self.registered_connections:
            return -1
        else:
            self.registered_connections[ws.get_id()] = ws
            return 1

    def un_register(self, who):
        del self.registered_connections[who]

    def tell_all(self, message):
        for k, v in self.registered_connections.iteritems():
            v.notify(message)

    def tell_all_protocol(self, protocol, message, fallback):
        for k, v in self.registered_connections.iteritems():
            v.notify_by_protocol(protocol, message, fallback)
        pass

    def tell_others(self, message, exclude):
        who = [v for k,v in self.registered_connections.iteritems() if k not in exclude]
        for v in who:
            v.notify(message)

    def tell_connection(self, message, who):
        who.notify(message)

    def tell_connection_protocol(self, who, protocol, message, fallback):
        who.notify_by_protocol(protocol, message, fallback)


    def tell_dbref(self, d, message):
        for k, v in self.registered_connections.iteritems():
            if v.dbref == d:
                v.notify(message)

    def tell_dbref_protocol(self, d, protocol, message, fallback):
        for k, v in self.registered_connections.iteritems():
            if v.dbref == d:
                v.notify_by_protocol(protocol, message, fallback)

    def get_all_connections(self):
        return self.registered_connections



global_connection_handler = ConnectionManager()
