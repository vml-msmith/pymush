import os
import unittest

from muse.db import DatabaseObject
from muse.db import Database
from muse.db import DatabasePersister
from muse.db import DB_TYPE_PLAYER

class DatabaseObjectProperties(unittest.TestCase):
    def test_has_property_method(self):
        object = DatabaseObject(1)
        self.assertIsNotNone(object.get_property('created'))

class DatabasePersistanceTests(unittest.TestCase):
    def setUp(self):
        self.file_name = 'db.sqlite'

    def tearDown(self):
        os.remove(self.file_name)

    def test_can_dump(self):
        db = Database()
        writer = DatabasePersister(self.file_name)
        writer.dump(db)

    def test_load_bad_database_returns_none(self):
        persistance = DatabasePersister(self.file_name)
        db = persistance.load()
        self.assertIsNone(db)

    def test_persistance_between_dump_load(self):
        db = Database()
        pre_object = DatabaseObject(1)
        pre_object.name = "Michael"
        db.store(pre_object)
        persistance = DatabasePersister(self.file_name)

        persistance.dump(db)
        db = persistance.load()
        object = db.find(1)
        self.assertEqual(object.ref, 1)
        self.assertEqual(object.name, 'Michael')

    def test_persistance_of_object_structure_data(self):
        db = Database()
        pre_object = DatabaseObject(1)
        pre_object.name = "Michael"
        pre_object.type = DB_TYPE_PLAYER

        db.store(pre_object)
        persistance = DatabasePersister(self.file_name)
        persistance.dump(db)
        db = persistance.load()
        object = db.find(1)
        self.assertEqual(object.name, 'Michael')
        self.assertEqual(object.type, DB_TYPE_PLAYER)

    def test_old_db_is_overwritten(self):
        db = Database()
        pre_object = DatabaseObject(2)
        pre_object.name = "Michael"
        db.store(pre_object)
        db.store(DatabaseObject(5))
        persistance = DatabasePersister(self.file_name)
        persistance.dump(db)
        persistance = DatabasePersister(self.file_name)
        db = persistance.load()
        self.assertIsNone(db.find(1))

class DatabaseObjectTests(unittest.TestCase):
    def test_has_id(self):
        object_1 = DatabaseObject(1)
        self.assertEqual(object_1.ref, 1)
    
    def test_has_name(self):
        object_1 = DatabaseObject(1)
        self.assertIsNot(object_1.name, None)

    def test_cannot_change_reference(self):
        object_1 = DatabaseObject(1)
        with self.assertRaises(AttributeError):
            object_1.ref = 5


    def test_has_type(self):
        object_1 = DatabaseObject(1)
        self.assertIsNot(object_1.type, None)


class DatabaseSaveAndFindTests(unittest.TestCase):
    def setUp(self):
        self.db = Database()
    def test_object_lookup(self):
        self.db.store(DatabaseObject(1))
        object_1 = self.db.find(1)
        self.assertEqual(object_1.ref, 1)

    def test_object_lookup_bad_object(self):
        object_1 = self.db.find(1)
        self.assertIsNone(object_1)

    def test_object_save_multiple(self):
        object_1 = DatabaseObject(1)
        self.db.store(object_1)
        found_object = self.db.find(1)
        self.assertEqual(found_object.ref, object_1.ref)

        object_2 = DatabaseObject(2)
        self.db.store(object_2)
        found_object = self.db.find(2)
        self.assertEqual(found_object.ref, object_2.ref)

    def test_stored_and_found_objects_are_same_object(self):
        db = Database()
        object_1 = DatabaseObject(1)
        object_1.name = "Random Object Name"
        db.store(object_1)
        object_2 = db.find(1)
        object_2.name = "Specific name"
        self.assertEqual(object_1.name, object_2.name)
        self.assertEqual(object_1.name, 'Specific name')


def main():
    unittest.main()

if __name__ == '__main__':
    main()
