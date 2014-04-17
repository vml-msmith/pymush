from muse.game import Game
from muse.game import GameTimer
from muse.game import GameConfig

import unittest

class MockGameTimer(GameTimer):
    def __init__(self):
        self.do_keep_running = True
        self.number_of_runs = 0;
        self.max_number_of_runs = 5;

    def keep_running(self):
        if (self.number_of_runs > self.max_number_of_runs):
            self.shutdown()

        self.number_of_runs += 1

        return super(MockGameTimer, self).keep_running()


class MockGameConfigObject(GameConfig):
    pass

'''
class MockSocketListener(object):
    def is_listening(self):
        return True
'''

class GameTimerTests(unittest.TestCase):
    def test_timer_exists(self):
        timer = GameTimer()
        self.assertIsInstance(timer, object)

    def test_keep_running_method(self):
        timer = GameTimer()
        response = timer.keep_running()
        self.assertTrue(response)

    def test_shutdown_stops_running(self):
        timer = GameTimer()
        timer.shutdown()
        self.assertFalse(timer.keep_running())


class GameObjectTests(unittest.TestCase):
    def test_game_class_exists(self):
        conf = MockGameConfigObject()
        game = Game(config=conf)
        self.assertIsInstance(game, Game)

    '''
    def test_start_network_connections(self):
        conf = MockGameConfigObject()
        conf.socket_listener = MockSocketListener()
        game = Game(config=conf)
        game.start_network_connections()
        self.assertIsInstance(game.network_listener, MockSocketListener)
        self.assertTrue(game.network_listener.is_listening())
    '''

    def test_takes_config_object(self):
        conf = MockGameConfigObject()
        game = Game(config=conf)
        self.assertEqual(game.config, conf)

    def test_no_config_on_init(self):
        game = Game()

    def test_inject_config(self):
        conf = MockGameConfigObject()
        game = Game()
        self.assertEqual(game.config, None)
        game.injectConfig(conf)
        self.assertEqual(game.config, conf)

    def test_start_before_run(self):
        conf = MockGameConfigObject()
        conf.game_timer = MockGameTimer()
        game = Game(conf)
        self.assertFalse(game.run())
        game.injectConfig(conf)
        game.start()
        self.assertTrue(game.run())

    def test_game_uses_timer(self):
        conf = MockGameConfigObject()
        conf.game_timer = MockGameTimer()
        game = Game(conf)
        game.start()

        for x in range(0, 6):
            self.assertTrue(game.run())

        self.assertFalse(game.run())