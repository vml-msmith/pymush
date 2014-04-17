from muse.network.descriptor import Descriptor
from muse.network.server import MuseWebSocket
from muse.network.network_mediator import network_mediator

import unittest

class MockSocket(MuseWebSocket):
    def __init__(self):
        self.output = []
        self.is_open = True

    def close(self):
        self.is_open = False

    def write_message(self, message):
        self.output.append(message)

    def get_output(self):
        if len(self.output) is 0:
            return None

        return self.output.pop(0)

    def get_recent_output(self):
        saved = None
        output = self.get_output()
        while output is not None:
            saved = output
            output = self.get_output()

        return saved

    def has_output_message_type(self, type):
        output = self.get_output()
        while output is not None:
            if output.message == type:
                return True
            output = self.get_output()

        return False


class DescriptorTests(unittest.TestCase):
    def test_descriptor_writes(self):
        socket = MockSocket()
        socket.open()

        ref = socket.who_is_your_descriptor()
        desc = network_mediator.ref_to_desc(ref)
        desc.send_raw("Test output")
        self.assertEquals(socket.get_recent_output(), "Test output")

    def test_send_empty(self):
        socket = MockSocket()
        socket.open()
        socket.on_message("")

    def test_send_blank(self):
        socket = MockSocket()
        socket.open()
        socket.on_message("     ")

    def test_send_long_string(self):
        string = "1" * 10000
        socket = MockSocket()
        socket.open()
        socket.on_message(string)


class WebSocketTests(unittest.TestCase):
    def test_websocketr_input(self):
        socket = MockSocket()
        socket.open()
        desc = socket.descriptor
        socket.on_message("Message")


class TestConnect(unittest.TestCase):
    def test_has_welcome_message(self):
        socket_1 = MockSocket()
        socket_1.open()
        self.assertTrue(socket_1.has_output_message_type("welcome"))

    def test_accepts_quit(self):
        socket_1 = MockSocket()
        socket_1.open()
        socket_1.on_message("QUIT");
        self.assertTrue(socket_1.has_output_message_type("disconnect"))
        self.assertFalse(socket_1.is_open)
