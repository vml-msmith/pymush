import sys
import cgi
#from db import global_database
from network.connections import global_connection_handler
from muse.environment import Environment

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


class ColorSequence(object):
    def __init__(self, string, point):
        self.sequence = string
        self.start = point
        self.end = None

    def setEnd(self, num):
        self.end = num

    def buildTag(self):
        sequence = self.sequence
        sequence_parts = sequence.split(':', 1)
        tag = ['<span']

        if sequence_parts[0] == 'class' and len(sequence_parts) > 1:
            tag.append(' class="')
            tag.append(sequence_parts[1])
        else:
            tag.append(' style="')
            tag.append(sequence)

        tag.append('">')

        return ''.join(tag)

    def buildEndTag(self):
        return '</span>'

class ColorString(unicode):
    colors = {
        'red': 'ansiRed',
        'red-hilite': '#900000',
        'green': 'ansiGreen',
        'green-hilite': '#33ff33'
    }
    def __new__(cls, *args, **kwargs):
        string = args[0]
        sequences = []
        end_sequences = []
        original = string
        my_string = string
        while True:
            start = my_string.find('x1b[')
            if start == -1:
                break

            end = my_string.find(']')
            sequence = my_string[start + 4:end]

            print sequence
            if sequence == 'end':

                end_sequences.append(ColorSequence(sequence, start))
                s = []
                while True:
                    last = sequences.pop()
                    s.append(last)
                    if last.end == None:
                        break;

                last.setEnd(start)
                while len(s) > 0:
                    sequences.append(s.pop())

                #print last.start
                #print last.end
            else:
                sequences.append(ColorSequence(sequence, start))

            my_string = str(my_string[0:start] + my_string[end + 1:])

        my_args = original,

        newobj = unicode.__new__(cls, *my_args, **kwargs)

        newobj.sequences = sequences
        newobj.end_sequences = end_sequences
        newobj.original = original
        newobj.parsed = my_string

        return newobj

    def wrap(self, sequence):
        return 'x1b[' + sequence + ']' + self + 'x1b[end]'

    def color(self, color):
        color = ''.join(('ansi',color.capitalize()))
        return self.wrap('class:' + color)

    def outString(self):

        out_string = self.parsed
        s_list = self.sequences
        s_list.reverse();

        string = list(out_string)
        string = [cgi.escape(i) for i in string]

        for s in s_list:

            string[s.start] = s.buildTag() +  string[s.start]
            if s.end >= len(string):
                string.append('')
            string[s.end - 1] = string[s.end - 1] + s.buildEndTag()

        return ''.join(string)

class TargetMatcher(object):
    def __init__(self):
        self.type = None

    def options(self, data):
        if 'type' in data:
            if isinstance(data['type'], tuple):
                self.type = data['type']
            else:
                self.type = (data['type'])

        return self

    def match(self, enactor, target_string):

        ustring = target_string.upper()
        if ustring == 'ME':
            return enactor
        elif ustring == 'HERE':
            return enactor.location
        elif DbrefFormatter().is_dbref(target_string) == True:
            item = global_database.get_object_by_dbref(target_string)

            if self.type == None or item == None or item.type in self.type:
                return item

        location = enactor.location

        for item in location.contents:
            item_name = item.name.upper()

            if item_name == ustring and item.type in self.type:
                return item

        if location.type == 'Room':

            if self.type == None or 'Exit' in self.type:
                for item in location.exits:

                    item_name = item.name.upper()

                    if item_name == ustring:
                        return item

        return None

class DbrefFormatter(object):
    def format(self, dbref):
        return ColorString('#' + str(dbref))
    def is_dbref(self, dbref):
        if dbref[0] == '#' and is_number(dbref[1:]):
            return True
        return False

class NameFormatter(object):
    colors = {
        'Room' : 'green',
        'Thing' : 'blue',
        'Exit' : 'cyan',
        'Channel' : 'yellow',
        'Player' : 'red'
    }
    def __init__(self):
        self.looker = None
        self.full = True
        self.color = True

    def basic(self):
        self.full = False
        self.color = False
        return self

    def colorize(self):
        self.color = True
        return self

    def looker(self, object):
        self.looker = object
        return self

    def format(self, object):
        name = ColorString(object.name)
        if self.full == True:
            name = ColorString(name + ' (' + DbrefFormatter().format(object.dbref()) + ')')
            if object.type in self.colors:
                name = name.color(self.colors[object.type])

        return name

#class Utility:
def stringify(arg):
    if isinstance(arg, basestring):
        return arg

    return str(arg).rstrip('0').rstrip('.')

if __name__ == "__main__":
    input = ''
    for arg in sys.argv:
        if arg != 'utility.py':
            input = input + arg + ' '
    input = input.rstrip()

    myString = ColorString(input)
    myString.wrap('color:uppercase')
    print myString.outString()
    print myString
