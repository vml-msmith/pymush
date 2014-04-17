from parser import Lexxer
from parser import Parser
from parser import Executor

class CodeRunner(object):
    deafults = {
        'enactor',
    }

    def __init__(self, details):
        for k, v in details.iteritems():
            setattr(self, k, v)

    def execute(self, code):
        lex = Lexxer().lex(code)
        parser = Parser().parse(lex)
        out = Executor().execute(parser)
        return out
