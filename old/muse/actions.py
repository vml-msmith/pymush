""" This module provides the 'Actions' an object on the server can make.
"""
from muse.notifier import Notifier
from muse.utility import ColorString
from muse.utility import NameFormatter

from muse.coderunner import CodeRunner
from muse.db import global_database


class Action(object):
    """
    This is the base class for all Actions that a DB object can make

    Every action that a DB object can make, be it through a trigger, cron or
    descriptor input, should have it's own class that is derived from this one.

    Each action should declare a default set of values it'll use to enact
    itself in the __init__() method AFTER calling the Action __init__ method.

    Any values that the action can use that may differ from action to action
    should be setup in the _setup() method that takes a dict of values, the
    keys being what the action can use.
    """

    def __init__(self, db_object):
        """ Set db_object as self.object """
        self.object = db_object

    def setup(self, data=None):
        """ Takes a dict of values and stores them on the object for use """
        if type(data) == dict:
            self._setup(data)

        return self

    def enact(self):
        """ Do whatever it is the Action does. Return nothing. """
        pass

class ActionAttributeSet(Action):
    """
    Cause one object to set an attribute on an object.
    """
    def __init__(self, db_object):
        super(ActionAttributeSet, self).__init__(db_object)
        self.what = None
        self.attribute = None
        self.value = None

    def enact(self):
        self.what.set_attribute(self.attribute, self.value)
        Notifier().notify(self.object, "Attribute set.")

    def _setup(self, data):
        for attr in ('what', 'attribute', 'value'):
            if attr in data:
                setattr(self, attr, data[attr])


class ActionConnect(Action):
    """
    Run anything associated with 'Connecting'.

    Connecting is when a DB object (should always be a Player) is connected
    to a descriptor. A lot of things can happen. The connecting player is shown
    connection messages, connect softcode is called, announcements are made
    and the player implicitly 'looks'.
    """
    def enact(self):
        ActionLook(self.object).enact()

class ActionTeleport(Action):
    def __init__(self, db_object):
        super(ActionTeleport, self).__init__(db_object)
        self.what = None
        self.where= None

    def enact(self):
        where = self.where
        if self.where.type == 'Exit':
            where = self.where.location
            if where == None:
                where = self.where.home

        global_database.move_item(self.what, where)
        ActionLook(self.object).enact()

    def _setup(self, data):
        if 'what' in data:
            self.what = data['what']
        if 'where' in data:
            self.where = data['where']

class ActionDig(Action):
    def __init__(self, db_object):
        super(ActionDig, self).__init__(db_object)
        self.name = 'Generic Room'
        self.teleport = False
        self.exit_name = None
        self.return_exit_name = None

    def enact(self):
        room = global_database.create_room(self.name)

        Notifier().notify(self.object, ' '.join((
            NameFormatter().format(room),
            'has been dug.')))
        if self.exit_name != None:
            my_exit = global_database.create_exit(self.exit_name, self.object.location)
            Notifier().notify(self.object, ' '.join((
            NameFormatter().format(my_exit),
            'opened.')))
            global_database.move_item(my_exit, room)

        if self.return_exit_name != None:
            my_exit = global_database.create_exit(self.return_exit_name, room)
            Notifier().notify(self.object, ' '.join((
            NameFormatter().format(my_exit),
            'opened.')))
            global_database.move_item(my_exit, self.object.location)

        if self.teleport:
            ActionGoto(self.object).setup({'what' : room}).enact()

    def _setup(self, data):
        for attr in ('name', 'teleport',
                     'exit_name', 'return_exit_name'):
            if attr in data:
                setattr(self, attr, data[attr])

class ActionGoto(Action):
    def __init__(self, db_object):
        super(ActionGoto, self).__init__(db_object)
        self.what = None

    def enact(self):
        if self.what == None:
            self.what = self.object.location

        where = self.what

        if self.what.type == 'Exit':
            where = self.what.location
            if where == None:
                where = self.what.home


        global_database.move_item(self.object, where)
        ActionLook(self.object).enact()

    def _setup(self, data):
        if 'what' in data:
            self.what = data['what']

class ActionLook(Action):
    def __init__(self, db_object):
        super(ActionLook, self).__init__(db_object)
        self.what = None

    def enact(self):
        if self.what == None:
            self.what = self.object.location

        parts = []
        parts.append(NameFormatter().format(self.what))
        attributes = self.what.attributes
        if 'DESCRIPTION' in attributes:
            description = attributes['DESCRIPTION']
            result = CodeRunner({}).execute(description.get_value())
            parts.append(result)

        content = self.what.contents
        if self.object in content:
            content.remove(self.object)

        for item in content:
            if item.type == 'Exit':
                content.remove(item)

        if len(content) > 0:
            parts.append('Contents:')
            for object in content:
                parts.append(NameFormatter().basic().colorize().format(object));

        if self.what.type == 'Room':
            exits = self.what.exits
            if len(exits) > 0:
                parts.append('Obvious Exits:')
                for exit in exits:
                    parts.append(NameFormatter().basic().colorize().format(exit))


        Notifier().notify(self.object, ColorString('\n'.join(parts)))


    def _setup(self, data):
        if 'what' in data:
            self.what = data['what']


class ActionExamine(Action):
    def __init__(self, db_object):
        super(ActionExamine, self).__init__(db_object)
        self.what = None

    def enact(self):
        if self.what == None:
            self.what = self.object.location

        #description = ''
        attributes = self.what.attributes

        parts = []
        protocol_response = {}
        name = NameFormatter().format(self.what)
        parts.append(name)
        protocol_response['name'] = name
        protocol_response['attributes'] = None
        if attributes != None:
            protocol_response['attributes'] = {}
            for k, v in attributes.iteritems():
                protocol_response['attributes'][k] = v.get_value()
                parts.append(': '.join((k.upper(), v.get_value())))

        text_response = '\n'.join(parts)

        Notifier().notify_by_protocol(
            self.object,
            'examine',
            protocol_response,
            NameFormatter().format(self.what))


    def _setup(self, data):
        if 'what' in data:
            self.what = data['what']

class ActionSay(Action):
    def __init__(self, db_object):
        super(ActionSay, self).__init__(db_object)
        self.what = ''

    def enact(self):
        oemit = ''.join(
            (NameFormatter().basic().format(self.object),
             ColorString(''.join((' says, "', self.what, '"')))))

        pemit = ColorString('You say, "' + self.what + '"')

        Notifier().exclude(self.object).notify_surroundings(self.object, oemit)
        Notifier().notify(self.object, pemit)

    def _setup(self, data):
        if 'what' in data:
            self.what = data['what']

class ActionPose(Action):
    def __init__(self, db_object):
        super(ActionPose, self).__init__(db_object)
        self.what = ''

    def enact(self):

        emit = ColorString(
            ' '.join((NameFormatter().basic().format(self.object),
                      self.what)))

        Notifier().notify_surroundings(self.object, emit)

    def _setup(self, data):
        if 'what' in data:
            self.what = data['what']

class ActionSemiPose(Action):
    def __init__(self, db_object):
        super(ActionSemiPose, self).__init__(db_object)
        self.what = ''

    def enact(self):
        emit =  ColorString(''.join((NameFormatter().basic().format(self.object),
                                     self.what)))

        Notifier().notify_surroundings(self.object, emit)

    def _setup(self, data):
        if 'what' in data:
            self.what = data['what']
