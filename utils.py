# This file is part of ClIDE
# ClIDE - A live-modifiable command-line IDE that can accept commands as pseudocode  

# @author Andrew Phillips  
# @copyright 2017 Andrew Phillips <skeledrew@gmail.com>

# ClIDE is free software; you can redistribute it and/or
# modify it under the terms of the GNU AFFERO GENERAL PUBLIC LICENSE
# License as published by the Free Software Foundation; either
# version 3 of the License, or any later version.

# ClIDE is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU AFFERO GENERAL PUBLIC LICENSE for more details.

# You should have received a copy of the GNU Affero General Public
# License along with ClIDE.  If not, see <http://www.gnu.org/licenses/>.

'''

'''


from zlib import adler32
import inspect
import readline
import logging
import importlib
from constants import JAVA_CLASS_PATH
from ctypes import *
from contextlib import contextmanager
import functools
import re


autoclass = None
cast = None

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

def load_text(path):
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
    global autoclass

    if not autoclass:
        # first call
        global scp
        scp = load_module('jnius_config').set_classpath
        exec('scp("%s")' % JAVA_CLASS_PATH.replace(';', '","'), globals())
        autoclass = load_module('jnius').autoclass
        global cast
        cast = load_module('jnius').cast

    #if not autoclass: raise Exception('Cannot import Java class without autoclass.')

    if not name: name = jclass.split('.')[-1] if '.' in jclass else jclass
    jclass = eval('autoclass("%s")' % (jclass))
    if global_: exec('global %s; %s = jclass' % (name, name))
    return jclass

def load_module(mod):
    # load or reload a module

    try:
        #import re
        exec('importlib.reload(%s)' % mod, globals())

    except Exception as e:
        mod = eval('importlib.import_module(\'%s\')' % (mod))
        return mod
    return

def clean_ansi(text, remove=''):
    # remove ANSI control codes
    ANSI_CLEANER = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]")
    clean_text = ANSI_CLEANER.sub("", text)
    return clean_text

### Handles ALSA error messages ###
ERROR_HANDLER_FUNC = CFUNCTYPE(None, c_char_p, c_int, c_char_p, c_int, c_char_p)

def py_error_handler(filename, line, function, err, fmt):
    pass

c_error_handler = ERROR_HANDLER_FUNC(py_error_handler)

@contextmanager
def noalsaerr():
    asound = cdll.LoadLibrary('libasound.so')
    asound.snd_lib_error_set_handler(c_error_handler)
    yield
    asound.snd_lib_error_set_handler(None)

class Hook():

    @staticmethod
    def pre_func(func, pre):

        @functools.wraps(func)
        def run(*args, **kwargs):
            pre(*args, **kwargs)
            return func(*args, **kwargs)
        return run

    @staticmethod
    def post_func(func, post):

        @functools.wraps(func)
        def run(*args, **kwargs):
            result = func(*args, **kwargs)
            post(*args, **kwargs)
            return result
        return run

    @staticmethod
    def set(orig, mod, where):
        orig = where(orig, mod)
        return orig
