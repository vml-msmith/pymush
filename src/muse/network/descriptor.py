from muse.network.protocol import Protocol
from muse.network.network_mediator import network_mediator
from muse.network.network_mediator import network_mediator

class CommandParser(object):
    def __init__(self):
        self.all_commands = {}
        self.command_dictionary = {}
        self.command_alias = {}
        self.command_short_codes = {}

    def _registerCommand(self, command):
        self.command_dictionary[command.name] = command
        self.all_commands[command.name] = command

        for alias in command.alias:
            self.command_alias[alias] = command.name
            self.all_commands[alias] = command

        if command.short_code != None:
            self.command_short_codes[command.short_code] = command.name
            self.all_commands[command.short_code] = command

    def register(self, command):
        if isinstance(command, tuple):
            for cmd in command:
                self._registerCommand(cmd)
            return

        self._registerCommand(command)


    def lookup_by_name(self, command):
        if command in self.all_commands:
            return self.all_commands[command]

        cmds = {k:v for k,v in  self.all_commands.iteritems() if k.startswith(command)}

        if len(cmds) == 1:
            return cmds.popitem()[1]

        return None

    def lookup_by_alias(self, command):
        if command in self.command_alias:
            command = self.command_alias[command]
            return self.lookup_by_name(command)

        return None

    def lookup_by_short_code(self, code):
        if code in self.command_short_codes:
            command = self.command_short_codes[code]
            return self.lookup_by_name(command)

        return None

    def run(self, descriptor, command):
        cmd = self.lookup_by_name(command)

        if cmd == None:
            return False

        obj = cmd(descriptor, command)
        obj.run()
        return True

class NonLitCommandParser(CommandParser):
    def run(self, descriptor, input):
        original = input

        if len(input) == 0:
            return None

        short = input[0]
        short = self.lookup_by_short_code(short)

        if short != None:
            cmd = short
            input = cmd.name + ' ' + input[1:]
        else:
            command = input.split(None, 1)
            if len(command) == 0:
                return None

            command = command[0].split('/', 1)
            command = command[0]
            command = command.upper()
            cmd = self.lookup_by_name(command)

            if cmd == None:
                cmd = self.lookup_by_alias(command)

                if cmd == None:
                    return False
        print cmd
        obj = cmd(descriptor, input, original)
        if len(obj.complain) > 0:
            Notifier().notify(descriptor, obj.complain)
        else:
            obj.run()
        return True

class CommandParent(object):
    name = "DEFAULT"
    alias = []
    short_code = None
    allowed_switches = []
    disabled = False
    allow_all_switches = False

    def __init__(self, descriptor, command, original):
        self.complain = ''
        self.switches = []

        self.left_eq = ''
        self.right_eq = ''
        self.left_eq_args = []
        self.right_eq_args = []

        self.descriptor = descriptor
        self.input = command
        self.original_input = original
        self.parse_switches()
        self.parse_eq()
        self.parse_args()

        print self.switches

        print self.left_eq
        print self.left_eq_args

        print self.right_eq
        print self.right_eq_args

    def run(self):
        return True

    def break_up(self, input, delimeter=None, limit = None):
        args = { 'string' : input, 'count' : 0, 'args' : {} }
        if limit is None:
            args['args'] = input.split(delimeter)
        else:
            args['args'] = input.split(delimeter, limit)

        args['count'] = len(args['args'])
        return args

    def squish_args(self, args):
        i = 0
        while i < args['count']:
            args['args'][i] = args['args'][i].rstrip().lstrip()
            i = i + 1
        return args

    def parse_switches(self):
        parts = self.input.split(None, 1)
        cmd = parts[0]
        switches = cmd.split('/')

        if (len(switches) > 1):
            self.switches = switches[1:]

        if self.allow_all_switches != True:
            extra_list = [item for item in self.switches
                          if item not in self.allowed_switches]
            if extra_list:
                self.complain = self.name + ': Unknown switch ' + extra_list.pop()

    def parse_eq(self):
        parts = self.input.split(None, 1)
        parts = parts.pop()
        parts = parts.split('=', 1)

        if (len(parts) > 1):
            self.left_eq = parts[0].rstrip().lstrip()
            self.right_eq = parts[1].rstrip().lstrip()

    def parse_args(self):
        self.left_eq_args = self.left_eq.split(',')
        self.right_eq_args = self.right_eq.split(',')

class CommandQuit (CommandParent):
    name = "QUIT"

    def run(self):
        self.descriptor.do_quit()
        return True

class CommandWho (CommandParent):
    name = "WHO"

    def run(self):
        self.descriptor.notify("Who's on? Someone")
        return True


class CommandConnect (CommandParent):
    name = "CONNECT"

    def run(self):
        commands = self.input.split(None, 3)

        player = Player.find_by_name_and_pass(global_database, commands[1], commands[2])
        if player == None:
            self.descriptor.notify("That user or password doesn't exist.")
            return True

        self.descriptor.login(player)
        ActionConnect(player).enact()
        return True


class DescriptorCommandProcessorDict(NonLitCommandParser):
    def __init__(self):
        super(DescriptorCommandProcessorDict, self).__init__()
        self.register((
            CommandQuit,
            CommandWho,
        ))

class DescriptorCommandProcessor(object):
    cmd_dict = DescriptorCommandProcessorDict()

    def run(self, cmd, descriptor):
        return self.cmd_dict.run(descriptor, cmd)



class DescriptorLoginCommandProcessorDict(NonLitCommandParser):
    def __init__(self):
        super(DescriptorLoginCommandProcessorDict, self).__init__()
        self.register((
            CommandConnect,
        ))

class DescriptorLoginCommandProcessor(object):
    cmd_dict = DescriptorLoginCommandProcessorDict()

    def run(self, cmd, descriptor):
        return self.cmd_dict.run(descriptor, cmd)


class Descriptor(object):
    def _send_welcome(self):
        message = Protocol()
        message.payload(text = "Welcome to the game!", message = "welcome")
        self.send_raw(message)

    def _send_connect_instructions(self):
        message = Protocol()
        message.payload(text = "Welcome to the game!", message = "connect_instructions")
        self.send_raw(message)

    def do_quit(self):
        message = Protocol()
        message.payload(text = "DISCONNECT", message = "disconnect")
        self.send_raw(message)
        network_mediator.socket_send_close(self.socket)

    def __init__(self, socket):
        self.socket = socket
        self.name = None


    def open(self):
        self._send_welcome()
        self._send_connect_instructions()

    def send_raw(self, message):
        network_mediator.socket_message_send(self.socket, message.to_json())

    def send(self, message):
        protocol = Protocol()
        protocol.payload(text = message)
        self.socket.write_message(protocol.to_json())

    def receive(self, message):
        command_mediator.process(self, message);
        # Process descriptor only commands.
        processor = DescriptorCommandProcessor()
        if processor.run(message, self) == True:
            return

        # Cool. Now if we're logged out, offer up login commands.
        # Otherwise offer up real commands.
        processor = DescriptorLoginCommandProcessor()
        if processor.run(message, self) == True:
            return
