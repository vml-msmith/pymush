import sqlite3
import sys;
from muse.network.connections import global_connection_handler
import datetime
import unicodedata

def is_dbref(string):
    if type(string) is int:
        return False

    print len(string)
    if (len(string) < 2):
        return False

    if string[0] != '#':
        return False

    return True

def convert_string_to_dbref(string):
    dbref = string[1:]
    return int(dbref)

def convert_dbref_to_string(string):
    return '#' + string

class DatabaseAttribute(object):
    def __init__(self, name, value):
        self.name = name.upper()
        self.value = value

    def set_value(self, value):
        self.value = value

    def get_value(self):
        return self.value

class DatabaseObject(object):
    ref = None
    name = None
    location = None
    type = "Object"

    def __init__(self, ref):
        # Pull the info from the DB.
        self.ref = ref
        self.contents = []
        self.attributes = {}
        self.home = None
        self.location = None
        self.alias = []

    def load_data(self, options):
        if 'name' in options:
            self.name = options['name']
        if 'location' in options:
            self.location = options['location']
        if 'home' in options:
            self.home = options['home']
        if 'attributes' in options:
            pass
        if 'alias' in options:
            self.alias = options['alias']

    def set_attribute(self, key, value):
        # Always a string. If it's already set, we copy the value in.
        attr = None
        key = key.upper()
        if key in self.attributes:
            attr = self.attributes[key]
        else:
            attr = DatabaseAttribute(key, value)

        attr.set_value(value)
        self.attributes[key] = attr

    def name(self):
        return self.name

    def dbref(self):
        return self.ref

class Exit(DatabaseObject):
    type = "Exit"

    def __init__(self, ref):
        self.source = None
        self.destination = None
        super(Exit, self).__init__(ref)

class Room(DatabaseObject):
    type = "Room"

    def __init__(self, ref):
        self.exits = []
        self.entrances = []
        super(Room, self).__init__(ref)

class Player(DatabaseObject):
    type = 'Player'

    def __init__(self, ref):
        self.password = ''
        super(Player, self).__init__(ref)

    def load_data(self, options):
        if 'password' in options:
            self.password = options['password']
        super(Player, self).load_data(options)

    def match_by_name_and_pass(self, name, password):
        name = name.lower()

        if self.name.lower() == name and self.password == password:
            return True
        else:
            return False


    @staticmethod
    def find_by_name_and_pass(db, name, password):
        objects = db.get_all_objects_of_type('Player')

        if objects == None:
            return None

        for player in objects.itervalues():
            if player.match_by_name_and_pass(name, password) == True:
                return player

        return None

class Channel(DatabaseObject):
    type = "Channel"

    def __init__(self, ref):
        super(Channel, self).__init__(ref)

class Database(object):
    def __init__(self):
        self.all_objects = {}
        self.all_objects_by_type = {}
        self.high_ref = 0
        self.back_refs = []

    def register_object(self, object):
        object_type = object.type
        if object_type in self.all_objects_by_type:
            self.all_objects_by_type[object_type][object.ref] = object
        else:
            self.all_objects_by_type[object_type] = { object.ref : object }

        self.all_objects[object.ref] = object

        if object.ref > self.high_ref:
            self.high_ref = object.ref

        if object.ref in self.back_refs:
            self.back_refs.remove(object.ref)

    def get_all_objects_of_type(self, object_type):
        if object_type in self.all_objects_by_type:
            return self.all_objects_by_type[object_type]
        else:
            return None

    def get_object_by_dbref(self, dbref):
        if is_dbref(dbref):
            dbref = convert_string_to_dbref(dbref)

        if dbref in self.all_objects:
            return self.all_objects[dbref]
        return None

    def link_item(self, object, to):
        pass

    def move_item(self, object, to):
        current_loc = object.location
        if current_loc != None:
            if object in current_loc.contents:
                current_loc.contents.remove(object)

        object.location = to
        to.contents.append(object)

    def validate(self):
        for k, v in self.all_objects.iteritems():
            if v.location != None:
                lookup = self.get_object_by_dbref(v.location)

                v.location = lookup

            if v.home != None:
                lookup = self.get_object_by_dbref(v.home)
                v.home = lookup

            if v.location == None and v.type != 'Exit':
                v.location = v

            if v.type == 'Exit' and v.home != None:
                v.home.exits.append(v)

            if (v.location != None and v.type != 'Room'):
                v.location.contents.append(v)

            ref = 0
            while ref < self.high_ref:
                if ref not in self.all_objects:
                    self.back_refs.append(ref)
                ref = ref + 1

    def get_next_ref(self):
        if not self.back_refs:
            return self.high_ref + 1

        return back_refs[0]


    def create_room(self, name):
        ref = self.get_next_ref()
        room = Room(ref)
        room.load_data({'name' : name})
        self.register_object(room)
        return room

    def create_exit(self, name, loc):
        name_bits = name.split(';')
        name = name_bits[0]
        alias = []
        if len(name_bits) > 1:
            alias = name_bits[1:]

        ref = self.get_next_ref()
        exit = Exit(ref)
        exit.load_data({'name' : name, 'alias' : alias})
        exit.home = loc
        loc.exits.append(exit)
        exit.location = loc
        self.register_object(exit)
        return exit


class DatabaseSqlManager(object):
    def __init__(self, database, filename):
        self.database = database
        self.filename = filename
        self.last_dump = datetime.datetime.now()

    def dump(self):
        # Find the file.
        self.last_dump = datetime.datetime.now()
        conn = sqlite3.connect('example.db')
        conn.close()

    def get_last_dump(self):
        return self.last_dump


global_database = Database()
