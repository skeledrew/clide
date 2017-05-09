#! /usr/bin/python3


'''
PyShell
- A thin Python REPL providing additional functions (not quite anymore; to revise)
- Addons:
-- Session save/autosave/load
-- Input history
-- Output logging
-- Init templates
-- Allow multiline code correction and formatting
- Notes:
-- History functions from https://pymotw.com/2/readline/
'''


#from common import *
import pexpect
import sys
import importlib, inspect
import sh, shlex
from pyparsing import nestedExpr
import pdb
import os
from pyswip import *
from io import StringIO
import time
import readline


DEBUG = False
MAJOR = 0
MINOR = 0
BUILD = 4
OB = '<{'
CB = '}>'
QUIT = 'quit...'
PROMPT = '_'
JAVA_CLASS_PATH = '.;/home/skeledrew/Projects/htmlunit/2.26/lib/*'
INIT_FILE = 'clide.init'
WELCOME_MSG = 'Welcome to ClIDE, the Command-line IDE v%d.%d.%d\n' % (MAJOR, MINOR, BUILD)
COMMENT = '#'
INITD = False  # True if initialization file was successfully read
KDBASE = 'clide.pl'
USE_PDB = False
TMP_FILE = 'clide.tmp'
HIST_FILE = 'clide.hist'

autoclass = None
cast = None


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

def evalProlog(cmd, debug=False):
    if DEBUG: debug = True
    expList = [pexpect.EOF, pexpect.TIMEOUT, '\?-', '=']
    child = pexpect.spawnu('/bin/bash -c "swipl --quiet -s %s"' % KDBASE)
    child.logfile_read = open(TMP_FILE, 'w')
    asked = False
    answered = False

    while True:
        idx = child.expect(expList)
        time.sleep(0.5)
        if debug: print('DBG: pexpect got |%s|' % loadText(TMP_FILE))

        if idx == 2 and not asked:
            # at prompt
            if debug: print('DBG: got a prompt!')
            child.sendline(cmd)
            asked = True
            continue

        if idx == 2 and asked:
            # at another prompt
            if debug: print('DBG: another prompt...')
            return loadText(TMP_FILE)

        if idx == 13:
            # prob got all the result. NB: should be #3 targetting '.' but currently works w/out
            if debug: print('DBG: got dot in |%s|' % loadText(TMP_FILE))
            child.sendline('halt.')
            #return loadText(TMP_FILE)

        if idx == 3:
            # prob multiple bindings. should be #4
            if debug: print('DBG: multiple bindings')
            child.sendline(';')
            continue

        if idx == 5:
            # not sure
            print('Not sure if we should get here...')
            child.terminate()
            return None

def load(mod):
    # load or reload a module. Currently broken

    try:
        print('Attempting to load ' + mod)
        import re
        exec('importlib.reload(%s)' % mod, globals())

    except Exception as e:
        print('Error: %s; Falling back to import' % str(e))
        exec('%s = importlib.import_module(\'%s\')' % (mod, mod), globals())
    return

def pysh(cmd, debug=False):
    # takes a shell command as a string and runs it with shlex and sh
    if DEBUG: debug = True
    result = None
    if not type(cmd) == type('') or cmd == '': return None
    cmdList = shlex.split(cmd)
    if debug: print('DBG: cmdList = %s' % cmdList)
    cmd = 'sh.%s(' % cmdList[0]
    cmdList.remove(cmdList[0])

    if len(cmdList) > 0:

        for arg in cmdList:
            cmd += '"%s",' % arg
    cmd += ')'
    if debug: print('DBG: cmd = %s' % cmd)

    try:
        result = eval(cmd)

    except Exception as e:
        print('EvalError: ' + str(e))
    if debug: print('DBG: result = %s' % result)
    return result

def pesh(cmd, out=sys.stdout, shell='/bin/bash', debug=False):
    # takes command as a string or list
    result = ''
    if debug: print('DBG: cmd = \'%s\' & out = %s' % (cmd, str(out)))

    if out == False and type(out) == type(False):
        # run and forget; need multiprocess to prevent pexpect killing or blocking
        if debug: print('DBG: running in separate process')
        proc = Process(target=launch, args=([cmd, shell])).start()
        return 1
    child = pexpect.spawnu(shell, ['-c', cmd] if type(cmd) == type('') else cmd)

    if not out == sys.stdout:
        result = out
        out = open(TMP_FILE, 'w')
    child.logfile = out
    child.expect([pexpect.EOF, pexpect.TIMEOUT])  # command complete and exited
    #sleep(5)

    if not result == False and child.isalive():
        # block until the child exits (normal behavior)
        # otherwise, don't wait for a return
        print('Waiting for child process...')
        child.wait()

    if out == sys.stdout:
        # output went to standard out or not waiting for child to end
        return
    out.close()
    lines = []

    with open(TMP_FILE) as fo:

        for line in fo:
            lines.append(line.strip())
    if debug: print('DBG: lines = %s' % str(lines))

    if type(result) == type(0):
        # get line specified by number, or last line
        if result < len(lines): return str(lines[result])

    if result == 'all':
        # all lines
        return lines

    if type(result) == type(''):
        # get line specified by pattern

        for line in lines:

            if result in line:  # TODO: make into regex match
                return line
        return None

def readExpr(cmd='', debug=False):
    # Reads an expression from stdin and does basic validation

    while True:
        if not cmd: cmd = input(PROMPT)
        if cmd == '': continue
        if cmd.strip()[0] == COMMENT: return None
        cmd = nestedExpr(OB, CB).parseString('%s%s%s' % (OB, cmd, CB)).asList()[0]  # parse into list
        break
    return cmd

def evalExpr(_expr=None, level=0, debug=False):
    # Recursively evaluates expression as a - nested - list of strings
    expr = None if _expr == None else _expr[:]  # prevent recursive reference hell
    if DEBUG: debug = True
    if debug: print('DBG: processing nested, expr = %s, level = %d' % (str(expr), level))
    cmd = ''

    for item in expr:
        # process each list element at the current level
        if debug: print('DBG: item = %s' % item)

        if type(item) == type([]):
            # process a nested list
            if debug: print('DBG: level = %d' % level)
            cmd += evalExpr(item, level=level+1) + ' '

        else:
            cmd += item + ' '
    cmd = cmd.strip()
    if debug: print('DBG: processed nest, cmd = |%s|' % cmd)
    if debug: print('DBG: expr = %s & level = %d' % (expr, level))
    if level == 0 and cmd == QUIT: return QUIT
    result = None
    success = False
    if USE_PDB: pdb.set_trace()

    try:

        #if expr and cmd == QUIT: return cmd

        if cmd[0] == '>':
            # execute as Python

            try:
                result = eval(cmd[1:].strip())
                if debug: print('DBG: python eval\'d %s and got %s' % (cmd, result))
                if not result: result = True

            except:
                exec(cmd[1:].strip(), globals())
                if debug: print('DBG: exec\'d %s' % cmd)
                result = True
            #if debug: print('DBG: python result = %s' % result)
            success = True

        if cmd[0] == '(':
            # execute as Hy
            #if cmd[1] in '>$': return cmd  # not to be eval'd with Hy
            if not 'print' in cmd: cmd = '(print %s)' % cmd  # wrap with print to trigger return
            result = sh.hy('-c', cmd)
            if debug: print('DBG: hy result = %s' % result)
            success = True

        if cmd[0] == '$':
            # execute as Shell
            result = pysh(cmd[1:].strip())
            if debug: print('DBG: shell result = %s' % result)
            success = True

        if cmd[0] == '?' or cmd[-1] == '.':
            # execute as Prolog
            if cmd[0] == '?': cmd = cmd[1:].strip()
            if not cmd[-1] == '.': cmd += '.'
            if debug: print('cmd = "%s", KDBASE = %s' % (cmd, KDBASE))
            #result = pesh('swipl -s %s -g "%s" -t halt' % (KDBASE, cmd), 0)
            result = evalProlog(cmd)
            if debug: print('DBG: prolog result = %s' % result)
            success = True

        if success: return str(result)
        print('Error: Unable to resolve "%s"; Check the command syntax.' % cmd)

    except Exception as e:
        if debug: raise
        print('ExecError: ' + str(e))
        return str(None)

def repl(_expr=None, debug=False):
    if DEBUG: debug = True
    initEnv()
    if os.path.exists(HIST_FILE): readline.read_history_file(HIST_FILE)
    global autoclass

    if not autoclass:
        # first run
        global scp
        scp = importlib.import_module('jnius_config').set_classpath
        exec('scp("%s")' % JAVA_CLASS_PATH.replace(';', '","'), globals())
        autoclass = importlib.import_module('jnius').autoclass
        global cast
        cast = importlib.import_module('jnius').cast
        if debug: print('DBG: autoclass = %s' % autoclass)
        print(WELCOME_MSG)

    while True:
        expr = readExpr()
        result = evalExpr(expr)
        if result == QUIT: break
        print(result)
    readline.write_history_file(HIST_FILE)
    print('Goodbye cruel world :\'(')

def initEnv():
    # Initialize the environment with commands from a file
    readline.set_completer(HistoryCompleter().complete)
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set enable-keypad on')

    if not os.path.isfile(INIT_FILE): return

    with open(INIT_FILE) as fo:

        for line in fo:
            cmd = readExpr(line)
            if cmd: evalExpr(cmd)
    return

if __name__ == '__main__':
    repl()
