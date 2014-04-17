import tornado.websocket
import os.path

from tornado import gen
from tornado.options import define, options, parse_command_line
from descriptor import Descriptor

class WSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        self.descriptor = Descriptor(self)

    def on_message(self, message):
        print message
        self.descriptor.input(message)

    def on_close(self):
        self.descriptor.disconnect()

class Listener:
    def setup(self, port):
        self.listener = None
        self.listener = tornado.web.Application(
            [
                (r'/', WSHandler),
            ],
            template_path=os.path.dirname(__file__),
            static_path=os.path.dirname(__file__),
        )
        self.listener.listen(port)

    def start(self):
        tornado.ioloop.IOLoop.instance().start()

    def stop(self):
        tornado.ioloop.IOLoop.instance().stop()
