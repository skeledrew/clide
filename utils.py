'''

'''


from zlib import adler32
import inspect
import readline
import logging
import importlib


def members(itm):

    for mem in inspect.getmembers(itm):
        print(mem)
    return

def hash_sum(data):
    return adler32(bytes(data, 'utf-8'))

def get_history_items():
    return [ readline.get_history_item(i)
             for i in xrange(1, readline.get_current_history_length() + 1)
             ]

class HistoryCompleter(object):

    def __init__(self):
        self.matches = []
        return

    def complete(self, text, state):
        response = None
        if state == 0:
            history_values = get_history_items()
            logging.debug('history: %s', history_values)
            if text:
                self.matches = sorted(h 
                                      for h in history_values 
                                      if h and h.startswith(text))
            else:
                self.matches = []
            logging.debug('matches: %s', self.matches)
        try:
            response = self.matches[state]
        except IndexError:
            response = None
        logging.debug('complete(%s, %s) => %s', 
                      repr(text), state, repr(response))
        return response

def loadText(path):
    text = ''

    with open(path) as f:

        for line in f:
            text += line
    return text

def gen_name(pre='tmp', size=4, char='0', namespace=globals()):
    '''Generate a unique temporary global variable

:parameters:
-  `name` (type) - <desc>

:returns: <desc>
:rtype:
(str)

:created: 17-05-11
:modified: 17-05-11
:author: <detail>

.. notes:: <text>

.. todo:: <text>

.. changes:: <text>
'''
    varname = ''

    for num in range(9999):
        # find a unique name
        varname = pre + str(num).rjust(size, char)
        if varname in namespace: continue
        exec('global %s; %s = None' % (varname, varname))
        break
    return varname

def j_import(jclass, name='', global_=True):
    # import a Java class
    if not autoclass: raise Exception('Cannot import Java class without autoclass.')

    if not name: name = jclass.split('.')[-1] if '.' in jclass else jclass
    jclass = eval('autoclass("%s")' % (jclass))
    if global_: exec('global %s; %s = jclass' % (name, name))
    return eval('name')

def load_module(mod):
    # load or reload a module. Currently broken

    try:
        #import re
        exec('importlib.reload(%s)' % mod, globals())

    except Exception as e:
        mod = eval('importlib.import_module(\'%s\')' % (mod))
        return mod
    return

