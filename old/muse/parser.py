import Queue
import sys
from math import fabs
from utility import stringify

def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass

    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass

    return False


def isSeparator(i):
    if i == ',':
        return True
    return False


def  isDown(i):
    if i == '(':
        return i
    return False

def isUp(i):
    if i == ')':
        return i
    return False

def isParcelIn(i):
    if i == '[':
        return i
    return False

def isParcelOut(i):
    if i == ']':
        return i
    return False

def isString(i):
    if isUp(i) == False and isDown(i) == False and isSeparator(i) == False and i != None and isParcelOut(i) == False and isParcelIn(i) == False:
        return True
    return False

def isReplacer(i):
    if i == '%':
        return True
    return False

def isSpace(i):
    if i == ' ':
        return True
    return False

class Lexxer(object):
    TOKEN_TYPE_UP = 'UP'
    TOKEN_TYPE_DOWN = 'DOWN'
    TOKEN_TYPE_STRING = 'STRING'
    TOKEN_TYPE_SEPARATOR = 'SEPARATOR'
    TOKEN_TYPE_REPLACER = 'REPLACER'
    TOKEN_TYPE_PARCEL_IN = 'PARCEL_IN'
    TOKEN_TYPE_PARCEL_OUT = 'PARCEL_OUT'

    FUN_NOT_FOUND =  "#-1 NO COMMAND FOUND"


    def __init__(self):
        self.tree = Queue.Queue()
        self.counter = -1
        self.code_string = None

    def lex(self, code):
        self.code_string = code;

        str = self.advance()

        while str != None:
            if isUp(str):
                self.addToken(self.TOKEN_TYPE_UP, str)
            elif isDown(str):
                self.addToken(self.TOKEN_TYPE_DOWN, str)
            elif isParcelIn(str):
                self.addToken(self.TOKEN_TYPE_PARCEL_IN, str)
            elif isParcelOut(str):
                self.addToken(self.TOKEN_TYPE_PARCEL_OUT, str)
            elif isSeparator(str):
                self.addToken(self.TOKEN_TYPE_SEPARATOR, str)
            elif isReplacer(str):
                next = self.advance()
                if isRplacer(next):
                    self.addToken(self.TOKEN_TYPE_STRING, str)
                else:
                    self.addToken(self.TOKEN_TYPE_REPLACER, str)
            else:
                next = self.advance()
                while isString(next):
                    str = str + next
                    next = self.advance()
                self.retract()
                self.addToken(self.TOKEN_TYPE_STRING, str)

            str = self.advance()

        return self.tree

    def createTree(self):
        self.tree = Queue.Queue()

    def addToken(self, type, value):
        self.tree.put_nowait({'value' : value, 'type' : type})

    def retract(self):
        self.counter = self.counter - 1
        return self.code_string[self.counter]

    def advance(self):
        self.counter = self.counter + 1

        if self.counter >= len(self.code_string):
            return None

        return self.code_string[self.counter]

class Parser(object):
    def setupTree(self):

        self.tree = { }
        self.level = self.tree
        self.parcel = None
        # self.addParcel()

    def addParcel(self):
        if 'parcelCount' not in self.level:
            self.level['parcelCount'] = 0

        self.level['parcelCount'] = self.level['parcelCount'] + 1

        if 'parcels' not in self.level:
            self.level['parcels'] = { }

        self.level['parcels'][self.level['parcelCount']] = {
            'argc' : 0,
            'method' : None,
            'args' : {},
            'parent' : self.level
        }

        self.parcel = self.level['parcels'][self.level['parcelCount']]


    def closeParcel(self):
        self.level = self.level['parent']
        self.parcel = self.level['parcels'][self.level['parcelCount']]

    def descend(self):
        # If we don't have a parcel yet, descending is an implicit parcel creation.
        if self.parcel == None:
            self.addParcel()

        self.parcel['argc'] = self.parcel['argc'] + 1

        self.parcel['args'][self.parcel['argc']] = { }
        self.parcel['args'][self.parcel['argc']]['parent'] = self.level
        self.level = self.parcel['args'][self.parcel['argc']]
        self.addParcel()

    def ascend(self):
        self.level = self.parcel['parent']
        self.parcel = self.level['parcels'][self.level['parcelCount']]
        #self.level = self.parcel['parent']
        #self.parcel = self.level['parcels'][self.level['parcelCount']]


    def insertMethod(self, method):
        if self.parcel == None:
            self.addParcel()

        self.parcel['method'] = method

    def parse(self, lex):
        self.setupTree()

        while lex.empty() == False:
            part = lex.get(False)
            while True:
                if part['type'] == Lexxer.TOKEN_TYPE_DOWN:
                    self.descend()
                elif part['type'] == Lexxer.TOKEN_TYPE_UP:
                    self.ascend()
                elif part['type'] == Lexxer.TOKEN_TYPE_SEPARATOR:
                    self.ascend()
                    self.closeParcel()
                    self.descend()
                elif part['type'] == Lexxer.TOKEN_TYPE_PARCEL_IN:
                    self.addParcel()
                elif part['type'] == Lexxer.TOKEN_TYPE_PARCEL_OUT:
                    self.closeParcel()
                else:
                    self.insertMethod(part['value'])

                break


            lex.task_done()

        return self.tree


class Function(object):
    def run(self, args):
        pass

class FunctionAdd(Function):
    def run(self, args):
        result = float(0)
        for ka, kv in enumerate(args):
            if (is_number(kv) == False):
                kv = 0
            result = result + float(kv)

        return stringify(result)

class FunctionAbs(Function):
    def run(self, args):
        if len(args) > 1:
            return "#-1 TOO MANY ARGS"

        arg = args[0]
        if isinstance(arg, basestring):
            arg = float(arg)

        return stringify(fabs(arg))

global_funcs = {
    'add': FunctionAdd,
    'abs': FunctionAbs,
}

class Executor(object):
    def execute(self, tree):
        self.tree = tree

        items = self.doParcels(tree['parcels'])
        return items

    def doParcels(self, parcels):
        bits = ''
        for k, v in parcels.iteritems():
            if v['argc'] == 0:
                if v['method'] != None:
                    bits = bits + ' ' + str(v['method'])
            else:
                args = []
                for key, value in v['args'].iteritems():
                    if (is_number(key)):
                        args.append(self.doParcels(value['parcels']))

                method = v['method'].lower()
                if method in global_funcs:
                    bits = bits + global_funcs[method]().run(args)
                else:
                    bits = bits + '#-1'


        return bits.rstrip().lstrip()


if __name__ == "__main__":
    input = ''
    for arg in sys.argv:
        if arg != 'parser.py':
            input = input + arg + ' '
    input = input.rstrip()

    lex = Lexxer().lex(input)
    parse = Parser().parse(lex)
    print Executor().execute(parse)
