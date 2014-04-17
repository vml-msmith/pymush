from muse.game import Game
from muse.game import GameTimer
from muse.game import GameConfig
from muse.network.server import Server


class InstanceConfig(GameConfig):
    def __init__(self):
        self.port = 1701
        self.game_timer = GameTimer()

if __name__ == "__main__":
    conf = InstanceConfig()
    game = Game(conf)
    server = Server()
    server.start(conf.port, game)
    server.runLoop()