class NetworkMediator(object):
    def _register_socket(self, socket):
        import weakref
        from muse.network.descriptor import Descriptor
        ref = weakref.ref(socket)
        desc = Descriptor(ref)

        self.connections[ref] = (socket, desc)
        desc.open()
        return ref

    def __init__(self):
        self.connections = {}

    def ref_to_socket(self, ref):
        return self.connections[ref][0]

    def ref_to_desc(self, ref):
        return self.connections[ref][1]

    def socket_connect(self, socket):        
        socket.register_descriptor(self._register_socket(socket))

    def socket_message_received(self, socket, message):
        ref = socket.who_is_your_descriptor()
        desc = self.ref_to_desc(ref)
        desc.receive(message)

    def socket_message_send(self, ref, message):
        socket = self.ref_to_socket(ref)
        socket.write_message(message)

    def socket_send_close(self, ref):
        socket = self.ref_to_socket(ref)
        socket.close()

network_mediator = NetworkMediator()
