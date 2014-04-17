'''
Database and database persistance classes.
'''
DB_TYPE_PLAYER = 'Player'
DB_TYPE_ROOM = 'Room'
DB_TYPE_THING = 'Thing'
DB_TYPE_EXIT = 'Exit'


class DatabaseObject(object):
    '''Represents an individual DatabaseObject, such as a Player, Room, Thing
    or Exit.
    '''

    @property
    def ref(self):
        '''Return the reference id of this object. '''

        return self._ref

    def __init__(self, ref):
        self._ref = ref
        self.name = "Some name"
        self.properties = {'created' : 'test'}
        self.type = DB_TYPE_THING

    def get_property(self, prop):
        '''Get a property from the object.

        A property is something that needs to be stored on this object, but is
        not a user editable attribute. That is, these values can't be set
        from &attr object = whatevs.
        '''

        return self.properties.get(prop, None)

class Database(object):
    '''The storage container that keeps track DatabaseObjects.'''
    def __init__(self):
        self.objects = {}

    def find(self, ref):
        '''Find and return a DatabaseObject by it's dbref

        Return None if the dbref isn't found.
        '''
        return self.objects.get(ref, None)

    def store(self, db_object):
        '''Store DatabaseObject in this database.'''
        self.objects[db_object.ref] = db_object


class DatabasePersister(object):
    '''Provides the persistance layer of dumping and loading database as
    .sqlite files.
    '''

    def _build_object_schema(self, cursor):
        '''Build the schema for objects table'''
        cursor.execute('DROP TABLE IF EXISTS objects')
        cursor.execute('''CREATE TABLE objects
        (id INT, name TEXT, type TEXT)''')

    def __init__(self, file_name):
        self.file_name = file_name

    def dump(self, database):
        '''Dump the Database to an sqlite3 db file.'''

        import sqlite3
        conn = sqlite3.connect(self.file_name)
        cursor = conn.cursor()

        self._build_object_schema(cursor)

        object_data = [(ref, obj.name, obj.type)
                       for (ref, obj)
                       in database.objects.iteritems()]

        cursor.executemany("INSERT INTO objects VALUES(?,?,?)",
                      object_data)

        conn.commit()

    def load(self):
        '''Load and return a database from an sqlite3 db file.

        All DatabaseObjects contained in the Database will be
        created as well.
        '''
        import sqlite3

        conn = sqlite3.connect(self.file_name)
        cursor = conn.cursor()

        try:
            database = Database()
            for row in cursor.execute('SELECT id, name, type FROM objects'):
                db_object = DatabaseObject(row[0])
                db_object.name = row[1]
                db_object.type = row[2]
                database.store(db_object)

                return database
        except sqlite3.OperationalError:
            return None
