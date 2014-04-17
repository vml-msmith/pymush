import signal
import logging

from muse.command import setup_commands

import datetime
from datetime import timedelta

from muse.db import Player
from muse.db import Room
from muse.db import Exit
from muse.db import DatabaseSqlManager
from muse.environment import Environment
from muse.commandqueue import global_command_queue
from muse.utility import TargetMatcher
import tornado.websocket

from parser import Lexxer
from parser import Parser
from parser import Executor

#from  muse.db import Player

from  muse.db import global_database

from network.socket import Listener


# create logger with 'spam_application'
logger = logging.getLogger()
def setup_logger():
    logger.setLevel(logging.DEBUG)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('game.log')
    fh.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s:  %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

setup_logger()


class Game(object):
    def shutdown(self):
        logging.info("Shutting down.")
        self.is_shutdown = True

    def real_shutdown(self):
        self.listener.stop()

    def handler(self, signum, frame):
        self.shutdown()

    def __init__(self):
        signal.signal(signal.SIGINT, self.handler)
        self.is_shutdown = False

    def init_websockets(self):
        self.listener = Listener()
        self.listener.setup(1701)
        self.db_manager = DatabaseSqlManager(global_database, 'somefile.db')

    def load_database(self):
        room_zero = Room(0)
        room_zero.load_data({'name' : 'Room Zero'})
        room_zero.set_attribute('description', 'This is a room [add(1,1)].')
        room_zero.set_attribute('first', 'data')
        room_zero.set_attribute('next', 'more data')

        player_one = Player(1)
        player_one.load_data({'name' : 'Michael', 'password' : 'Dnkroz', 'location' : 0})
        othic  = Player(2)
        othic.load_data({'name' : 'Othic', 'password' : 'Dnkroz', 'location' : 0})

        master_room = Room(3)
        master_room.load_data({'name' : 'Master Room'})

        door = Exit(4)
        door.load_data({'name' : 'My Door', 'home' : 0, 'location' : 3})

        global_database.register_object(room_zero)
        global_database.register_object(player_one)
        global_database.register_object(othic)
        global_database.register_object(master_room)
        global_database.register_object(door)

    def validate_database(self):
        global_database.validate()

    def init_db(self):
        self.load_database()
        self.validate_database()

    def start(self):
        setup_commands()
        self.init_websockets()
        self.init_db()

    def run(self):
        self.main_loop()
        self.listener.start()

    def process_commands(self):
        if global_command_queue.empty() == True:
            return False
        command = global_command_queue.get(False)
        if command == None:
            return False

        out = command.command
        if command.command[0] == '[':
            lex = Lexxer().lex(command.command)
            parser = Parser().parse(lex)

            out = Executor().execute(parser)

        if Environment.commands['connected'].run(command.object, out) == False:
            # We couldn't find a hard coded command. Next we try exits.
            exits = TargetMatcher().options({'type' : 'Exit'}).match(command.object, out)
            if exits != None:
                Environment.commands['connected'].run(command.object, "GO " + out)
            else:
                Environment.commands['connected'].run(command.object, "HUH")

        global_command_queue.task_done()
        return True


    def main_loop(self):
        if self.is_shutdown == True:
            return self.real_shutdown()

        start_time = datetime.datetime.now();
        self.process_commands()


        db_time = start_time - self.db_manager.get_last_dump()

        if db_time.seconds >= 10:
            self.db_manager.dump()

        elapsed_time = datetime.datetime.now() - start_time
        ms = 150000 - elapsed_time.microseconds
        d = timedelta(microseconds=ms)
        tornado.ioloop.IOLoop.instance().add_timeout(d, self.main_loop)
