class GameTimer(object):
    ''' Controls the timing of the game loop. At the moment all it's
    good for is telling us if we should keep running or not.
    '''

    def __init__(self):
        ''' Initialize the properties of the object.'''
        self.do_keep_running = True

    def shutdown(self):
        self.do_keep_running = False

    def keep_running(self):
        return self.do_keep_running


class GameConfig(object):
    pass


class Game(object):
    def _setupAttributes(self):
        #self.network_listener = None
        self.game_timer = None

    def __init__(self, config=None):
        self.has_started = False

        self._setupAttributes()
        self.injectConfig(config)

    def injectConfig(self, config):
        self.config = config

    def run(self):
        if self.game_timer == None:
            return False

        return self.game_timer.keep_running()

    def start(self):
        self.game_timer = self.config.game_timer