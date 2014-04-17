import json

class Protocol(object):
    def __init__(self):
        self.data = { 'text' : None }
        self.message = None

    def payload(self, text = None, message = None):
        if text is not None:
            self.data['text'] = text

        if message is not None:
            self.message = message

    def to_json(self):
        my_object = {
            'protocol': "text",
            'code' : None,
            'message' : self.message,
            'data' : self.data,
        }

        return json.dumps(my_object)
