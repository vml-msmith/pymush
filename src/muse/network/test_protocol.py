from muse.network.protocol import Protocol

import unittest
import json

class ProtocolTests(unittest.TestCase):
    def test_protocol(self):
        print "Test"
        protocol = Protocol()

    def test_protocol_convert_to_json(self):
        protocol = Protocol()
        json_version = protocol.to_json()
        decoded = json.loads(json_version)

    def test_protocol_has_correct_structure(self):
        protocol = Protocol()
        json_version = protocol.to_json()
        decoded = json.loads(json_version)

        self.assertIn('protocol', decoded)
        self.assertIn('code', decoded)
        self.assertIn('message', decoded)
        self.assertIn('data', decoded)

    def test_generic_protocol_is_text(self):
        protocol = Protocol()
        json_version = protocol.to_json()
        decoded = json.loads(json_version)
        self.assertEquals(decoded['protocol'], 'text')

    def test_text_protocol_has_data(self):
        protocol = Protocol()
        protocol.payload(text="Test data")
        json_version = protocol.to_json()
        decoded = json.loads(json_version)
        self.assertIn('text', decoded['data'])
        self.assertEquals(decoded['data']['text'], "Test data")

    def test_text_protocol_message(self):
        protocol = Protocol()
        protocol.payload(text="Test data")
        json_version = protocol.to_json()
        decoded = json.loads(json_version)
        self.assertEquals(decoded['message'], None)
        protocol.payload(message="welcome screen")
        json_version = protocol.to_json()
        decoded = json.loads(json_version)
        self.assertEquals(decoded['message'], "welcome screen")
        self.assertEquals(decoded['data']['text'], "Test data")
