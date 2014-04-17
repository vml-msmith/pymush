import random
import string
import datetime
import cgi
import json

from muse.actions import ActionConnect
from muse.environment import Environment
from muse.network.connections import global_connection_handler
from muse.commandqueue import global_command_queue
from muse.commandqueue import CommandQueueObject
from muse.utility import ColorString

class ConnectionStatus(object):
    LoginScreen, Connected = range(2)

class Descriptor(object):

    def __init__ (self, socket):
        self.socket = None
        self.id  = None
        self.connection_status = None
        self.hostname = None
        self.ip_address = None
        self.dbref = None
        self.player_object = None
        self.connected_time = None
        self.last_time = None
        self.quota_count = None
        self.command_count = None
        self.hidden = None


        self.socket = socket
        self.create_id();
        global_connection_handler.register(self)
        self.reset()
        self.print_login_screen()

    def reset(self):
        self.update_last_time()
        self.connected_time = datetime.datetime.now()
        self.hidden = False
        self.command_count = 0
        self.quota_count = 3
        self.dbref = None
        self.player_object = None
        self.connection_status = ConnectionStatus.LoginScreen

    def update_last_time(self):
        self.last_time = datetime.datetime.now()

    def input(self, data):
        if len(data) < 1:
            return

        self.update_last_time()

        if Environment.commands['global'].run(self, data) == True:
            return True

        if self.connection_status == ConnectionStatus.Connected:
            global_command_queue.put(CommandQueueObject(self.player_object, data))
            return True
        else:
            if Environment.commands['conn_screen'].run(self, data) == True:
                return True

        print "Nothing to do with the command"

        return True
        handled = self.handle_basic_commands(data)
        if (handled):
            if self.connection_status == ConnectionStatus.Connected:
                print data
#                global_input_queue.add(InputMessage(self, data))
            else:
                self.handle_login_input(data)

    def handle_basic_commands(self, data):
        print data;

    def handle_login_input(self, data):
        print "Login Data: " + data
        self.print_login_screen()


    def print_login_screen(self):
        screen = u"""-------------------------------------------------------------------------------
                                 Welcome!
-------------------------------------------------------------------------------
Commands:
  connect guest..............................................Connect as a guest
  connect <username> <password>....................Connect as an existing users
  create <username> <password>................................Create a new user
  WHO............................................Show who's currently connected
  QUIT...............................................Disconnect from the server
  HELP................................................See our awesome help menu"""
        self.notify(screen)

    def notify(self, message):
        if isinstance(message, ColorString):
            message = message.outString()
        else:
            message = unicode(message)
            message = cgi.escape(message)

        json_obj = json.dumps({'event_type' : 'text', 'data' : {'message' : message}})

        self.socket.write_message(json_obj)

    def notify_by_protocol(self, protocol, data, fallback):
        if True:
            json_object = json.dumps({'event_type' : protocol, 'data' : data})
            self.socket.write_message(json_object)
        else:
            notify(fallback)

    def disconnect(self):
        print "Gone"
        global_connection_handler.un_register(self.get_id());

    def quit(self):
        self.socket.write_message("Good bye!")
        self.socket.close()

    def login(self, player):
        self.player_object = player
        self.dbref = player.dbref()
        self.connection_status = ConnectionStatus.Connected

    def create_id(self):
        self.id = ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(15))

    def get_id(self):
        return self.id
