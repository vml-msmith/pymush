import sqlite3

class DatabaseObject(object):
    def __init__(self, ref):
        # Pull the info from the DB.
        self.ref = ref
        self.name = None
        self.location = None

    def load_data(self, options):
        if 'name' in options:
            self.name = options['name']
        if 'location' in options:
            self.location = options['location']

    def name(self):
        return self.name

    def dbref(self):
        return self.dbref

class Player(DatabaseObject):
    type = "Player"

    def __init__(self, ref):
        self.password = None
        return super(Player, self).__init__(ref)

    def load_data(self, options):
        if 'password' in options:
            self.password = options['password']
        return super(Player, self).load_data(options)

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
        print objects
        for player in objects.itervalues():
            print player
            if player.match_by_name_and_pass(name, password) == True:
                return player
            else:
                return None


class Database(object):
    all_objects = {}
    all_objects_by_type = {}
    def __init__(self):
        print "Starting up DB."


    def register_object(self, object):
        object_type = object.type
        if object_type in self.all_objects_by_type:
            self.all_objects_by_type[object_type][object.ref] = object
        else:
            self.all_objects_by_type[object_type] = { object.ref : object }

        self.all_objects[object.ref] = object


    def get_all_objects_of_type(self, object_type):
        if object_type in self.all_objects_by_type:
            return self.all_objects_by_type[object_type]
        else:
            return None
