import tornado.websocket
import os.path

from muse.network.network_mediator import network_mediator

class MuseWebSocket(tornado.websocket.WebSocketHandler):
    def register_descriptor(self, descriptor):
        self.descriptor = descriptor

    def who_is_your_descriptor(self):
        return self.descriptor

    def open(self):
        network_mediator.socket_connect(self)

    def on_message(self, message):
        network_mediator.socket_message_received(self, message)

    def on_close(self):
        network_mediator.socket_disconnect()

class Server(object):
    def start(self, port, game):
        self.game = game
        self.listener = tornado.web.Application(
            [
                (r'/', MuseWebSocket),
            ],
            template_path=os.path.dirname(__file__),
            static_path=os.path.dirname(__file__),
        )
        self.listener.listen(port)
        tornado.ioloop.IOLoop.instance().start()

    def stop(self):
        tornado.ioloop.IOLoop.instance().stop()
        pass

    def runLoop(self):
        if (self.game.run() != False):
            tornado.ioloop.IOLoop.instance().add_timeout(d, self.runLoop)
        else:
            self.stop()
