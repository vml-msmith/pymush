from muse.environment import Environment
from muse.db import Player
from muse.db import global_database
from muse.actions import *
from muse.utility import TargetMatcher
from muse.network.connections import global_connection_handler

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
        self.descriptor.quit()
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

class CommandHuh (CommandParent):
    name = "HUH"

    def run(self):
        Notifier().notify(self.descriptor, "Huh? I don't know what you mean.")

class CommandSay (CommandParent):
    name = 'SAY'
    short_code = '"'

    def run(self):
        commands = self.input.split(None, 1)
        words = ''
        if len(commands) > 1:
            words = commands[1]

        action_args = {
            'what' : words
        }
        ActionSay(self.descriptor).setup(action_args).enact()

        return True

class CommandPose (CommandParent):
    name = "POSE"
    short_code = ":"

    def run(self):
        commands = self.input.split(None, 1)
        words = ''
        if len(commands) > 1:
            words = commands[1]

        action_args = {
            'what' : words
        }
        ActionPose(self.descriptor).setup(action_args).enact()

        return True

class CommandSemiPose (CommandParent):
    name = "SEMI-POSE"
    short_code = ";"

    def run(self):
        commands = self.input.split(None, 1)
        words = ''
        if len(commands) > 1:
            words = commands[1]

        action_args = {
            'what' : words
        }
        ActionSemiPose(self.descriptor).setup(action_args).enact()

        return True

class CommandThink (CommandParent):
    name = "THINK"
    alias = ['TH']

    def run(self):
        commands = self.input.split(None, 1)

        if len(commands) > 1:
            Notifier().notify(self.descriptor, commands[1])

        return True

class CommandLook (CommandParent):
    name = "LOOK"
    alias = ['L']

    def run(self):
        commands = self.input.split(None, 1)
        what = self.descriptor.location

        if len(commands) > 1:
            what = commands[1]

        if isinstance(what, basestring):
            what = TargetMatcher().match(self.descriptor, what)

        if what ==  None:
            Notifier().notify(self.descriptor, "I can't see that here.")
            return True

        action_args = {
            'what' : what
        }
        ActionLook(self.descriptor).setup(action_args).enact()

        return True

class CommandGoto (CommandParent):
    name = "GOTO"
    alias = ['GO', 'MOVE']

    def run(self):
        commands = self.input.split(None, 1)
        what = self.descriptor.location

        if len(commands) > 1:
            what = commands[1]

        if isinstance(what, basestring):
            what = TargetMatcher().options({'type' : 'Exit'}).match(self.descriptor, what)

        if what ==  None:
            Notifier().notify(self.descriptor, "You can't go that way.")
            return True

        action_args = {
            'what' : what
        }
        ActionGoto(self.descriptor).setup(action_args).enact()

        return True

class CommandExamine (CommandParent):
    name = "EXAMINE"
    alias = ['EX']

    def run(self):
        commands = self.input.split(None, 1)
        at = self.descriptor.location

        if len(commands) > 1:
            at = commands[1]

        at = TargetMatcher().match(self.descriptor, at)

        if at ==  None:
            Notifier().notify(self.descriptor, "I can't see that here.")
            return True

        action_args = {
            'what' : at
        }
        ActionExamine(self.descriptor).setup(action_args).enact()

class CommandSet(CommandParent):
    name = "@SET"
    short_code = '&'

    def run(self):
        args = self.break_up(self.input, None, 1)
        if args['count'] <= 1:
            Notifier().notify(self.descriptor, "I can't see that here.")
            return

        command = args['args'][1]
        args = self.break_up(command, '=', 1)
        args = self.squish_args(args)

        if args['count'] < 2 or args['args'][1] == '':
            Notifier().notify(self.descriptor, "What do you want to set?")
            return

        if self.original_input[0] == '&':
            #The command was entered as &attribute item=value. Rewrite it
            attr = args['args'][0].split(None,1)

            if len(attr) < 2:
                Notifier().notify(self.descriptor, "What do you want to set?")
                return

            args['args'][0] = attr[1]
            attr = attr[0]
            args['args'][1] = ':'.join((attr, args['args'][1]))

        at = TargetMatcher().match(self.descriptor, args['args'][0])
        if at ==  None:
            Notifier().notify(self.descriptor, "I can't see that here.")
            return True

        args = self.break_up(args['args'][1], ':', 1)
        args = self.squish_args(args)

        if args['count'] > 1:
            # Set an attribute.
            action_args = {
                'what' : at,
                'attribute' : args['args'][0],
                'value' : args['args'][1]
            }
            ActionAttributeSet(self.descriptor).setup(action_args).enact()
        else:
            # Set a flag
            Notifier().notify(self.descriptor, "Flags aren't implemented yet.")

class CommandDig(CommandParent):
    name = "@DIG"
    allowed_switches = ['teleport', 'tel']

    def run(self):
        if self.left_eq.split(None) == []:
            Notifier().notify(self.descriptor, "Dig what?")
            return

        action_args = {
            'name' : self.left_eq
        }
        if 'teleport' in self.switches or 'tel' in self.switches:
            action_args['teleport'] = True

        if self.right_eq.split(None) != []:
            # We have right hand args. They should be comma split.
            if len(self.right_eq_args) > 2:
                Notifier().notify(self.descriptor, self.name + ": Too many args given")
                return

            action_args['exit_name'] = self.right_eq_args[0]

            if len(self.right_eq_args) > 1:
                action_args['return_exit_name'] = self.right_eq_args[1]

        ActionDig(self.descriptor).setup(action_args).enact()

class CommandTeleport(CommandParent):
    name = "@TELEPORT"

    def run(self):
        if len(self.left_eq) == 0:
            Notifier().notify(self.descriptor, "Teleport what?")
            return
        what = self.left_eq

        if len(self.right_eq) == 0:
            Notifier().notify(self.descriptor, "To where?")
            return
        where = self.right_eq

        what = TargetMatcher().match(self.descriptor, what)
        where = TargetMatcher().match(self.descriptor, where)

        if what ==  None:
            Notifier().notify(self.descriptor, "I can't see that here.")
            return True
        if where ==  None:
            Notifier().notify(self.descriptor, "I don't know where you want to teleport that.")
            return True

        action_args = {
            'what' : what,
            'where' : where
        }

        ActionTeleport(self.descriptor).setup(action_args).enact()

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

class NonLitCommandParser (CommandParser):
    def run(self, descriptor, input):
        original = input

        short = input[0]
        short = self.lookup_by_short_code(short)

        if short != None:
            cmd = short
            input = cmd.name + ' ' + input[1:]
        else:
            command = input.split(None, 1)
            command = command[0].split('/', 1)[0]
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

def setup_commands():
    Environment.commands['global'] = NonLitCommandParser()
    Environment.commands['conn_screen'] = NonLitCommandParser()
    Environment.commands['connected'] = NonLitCommandParser()

    Environment.commands['global'].register((
        CommandQuit,
        CommandWho
    ))

    Environment.commands['conn_screen'].register((
        CommandConnect,
    ))

    Environment.commands['connected'].register((
        CommandDig,
        CommandExamine,
        CommandGoto,
        CommandHuh,
        CommandLook,
        CommandPose,
        CommandSay,
        CommandSemiPose,
        CommandSet,
        CommandTeleport,
        CommandThink
    ))
