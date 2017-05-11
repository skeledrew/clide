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
import logging
import debugging


DEBUG = False
MAJOR = 0
MINOR = 0
BUILD = 5
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
USE_HIST = 3  # 0 = none, 1 = save, 2 = load, 3 = all
IFF = ':=>'  # separate pseudolog head and body
CONJ = '&&&'  # conjunct 2 body parts
DISJ = '|||'  # disjunct 2 body parts
ALPHA_LOWER = ''.join([chr(i) for i in range(97, 123)])
ALPHA_UPPER = ''.join([chr(i) for i in range(65, 91)])
NUMBERS = ''.join([str(i) for i in range(0, 10)])
USE_TRACE = False

autoclass = None
cast = None
_last_shell_result = None
_last_prolog_result = None
_tracer = None

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

def evalPseudolang(cmd, debug=False):
    pass

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
        #if debug: print('DBG: pexpect got |%s|' % loadText(TMP_FILE))

        if idx == 2 and not asked:
            # at prompt
            #if debug: print('DBG: got a prompt!')
            child.sendline(cmd)
            asked = True
            continue

        if idx == 2 and asked:
            # at another prompt
            #if debug: print('DBG: another prompt...')
            return loadText(TMP_FILE)

        if idx == 13:
            # prob got all the result. NB: should be #3 targetting '.' but currently works w/out
            #if debug: print('DBG: got dot in |%s|' % loadText(TMP_FILE))
            child.sendline('halt.')
            #return loadText(TMP_FILE)

        if idx == 3:
            # prob multiple bindings. should be #4
            #if debug: print('DBG: multiple bindings')
            child.sendline(';')
            continue

        if idx == 5:
            # not sure
            print('Not sure if we should get here...')
            child.terminate()
            return None

def gen_temp(pre='tmp', size=4, char='0'):
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
    global_ = globals()
    varname = ''

    for num in range(9999):
        # find a unique name
        varname = pre + str(num).rjust(size, char)
        if varname in global_: continue
        exec('global %s; %s = None' % (varname, varname))
        break
    return varname

def jimport(jclass, name='', global_=True):
    # import a Java class
    if not autoclass: raise Exception('Cannot import Java class without autoclass.')

    if not name: name = jclass.split('.')[-1] if '.' in jclass else jclass
    jclass = eval('autoclass("%s")' % (jclass))
    if global_: exec('global %s; %s = jclass' % (name, name))
    return eval('name')

def loadModule(mod):
    # load or reload a module. Currently broken

    try:
        if DEBUG: print('DBG: Attempting to load ' + mod)
        #import re
        exec('importlib.reload(%s)' % mod, globals())

    except Exception as e:
        if DEBUG: print('DBG: Error: %s; Falling back to import' % str(e))
        mod = eval('importlib.import_module(\'%s\')' % (mod))
        return mod
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
    gotArg = True if cmd else False

    while True:
        if not cmd: cmd = input(PROMPT)
        cmd = cmd.strip()
        if not gotArg and cmd == '': continue
        if cmd[0] == COMMENT: return None
        cmd = nestedExpr(OB, CB).parseString('%s%s%s' % (OB, cmd, CB)).asList()[0]  # parse into list
        break
    return cmd

def evalExpr(_expr=None, level=0, debug=False):
    # Recursively evaluates expression as a - nested - list of strings
    expr = None if _expr == None else _expr[:]  # prevent recursive reference hell
    #if DEBUG: debug = True
    #if debug: print('DBG: processing nested, expr = %s, level = %d' % (str(expr), level))
    cmd = ''

    for item in expr:
        # process each list element at the current level
        #if debug: print('DBG: item = %s' % item)

        if type(item) == type([]):
            # process a nested list
            #if debug: print('DBG: level = %d' % level)
            cmd += evalExpr(item, level=level+1) + ' '

        else:
            cmd += item + ' '
    cmd = cmd.strip()
    #if debug: print('DBG: processed nest, cmd = |%s|' % cmd)
    #if debug: print('DBG: expr = %s & level = %d' % (expr, level))
    if level == 0 and cmd == QUIT: return QUIT
    result = None
    success = False
    if USE_PDB: pdb.set_trace()

    try:

        #if expr and cmd == QUIT: return cmd

        if cmd.startswith(OB) and cmd.endswith(CB):
            # top level enclosure
            pass

        if cmd[0] == '>':
            # execute as Python

            try:
                result = eval(cmd[1:].strip())
                #if debug: print('DBG: python eval\'d %s and got %s' % (cmd, result))
                if not result: result = True

            except:
                exec(cmd[1:].strip(), globals())
                #if debug: print('DBG: exec\'d %s' % cmd)
                result = True
            success = True

        if cmd[0] == '(':
            # execute as Hy
            #if cmd[1] in '>$': return cmd  # not to be eval'd with Hy
            if not 'print' in cmd: cmd = '(print %s)' % cmd  # wrap with print to trigger return
            result = sh.hy('-c', cmd)
            #if debug: print('DBG: hy result = %s' % result)
            success = True

        if cmd[0] == '$':
            # execute as Shell
            result = pysh(cmd[1:].strip())
            global _last_shell_result
            _last_shell_result = result
            #result = '"%s"' % result  # should fix embedded issue
            #if debug: print('DBG: shell result = %s' % result)
            success = True

        if cmd[0] == '?' or cmd[-1] == '.':
            # execute as Prolog; yields a boolean, string or list of bindings
            if cmd[0] == '?': cmd = cmd[1:].strip()
            if not cmd[-1] == '.': cmd += '.'
            #if debug: print('cmd = "%s", KDBASE = %s' % (cmd, KDBASE))
            #result = pesh('swipl -s %s -g "%s" -t halt' % (KDBASE, cmd), 0)
            raw = evalProlog(cmd)
            #if debug: print('DBG: prolog raw result = %s' % raw)

            if '\n' in raw:
                # will prob always be true
                raw = raw.split('\n')
                rare = []
                done = ''

                for line in raw:
                    # get rid of the chaff
                    if line.startswith('?-') or line.startswith('|') or len(line.strip()) < 3: continue
                    done += line + '\n'

                    if ' = ' in line:
                        # binding; TODO: upgrate to intelligent detection
                        line = line.split(' = ')
                        if line[1][-1] == ';' or line[1][-1] == '.': line[1] = line[1][:-1].strip()
                        rare.append({line[0]: line[1]})

                    else:
                        # other returns
                        rare.append(line[:-1].strip())
                result = rare if len(rare) > 1 else rare[0]  # return list or single
                result = done.strip()  # (alt) return string w/out final newline
                global _last_prolog_result
                _last_prolog_result = result

            else:
                # prob shouldn't get here
                print('Why are we here???')
                raise
            success = True

        if cmd.strip().endswith(IFF):
            # activate reader mode
            isNatLang = False
            accepted = ALPHA_LOWER + ' '
            cmd = cmd.strip()[:-3]

            for char in cmd:

                if not char in accepted:
                    raise Exception('Invalid character detected. Command should only include "%s"' % accepted)
            isNatLang = True

        if cmd.strip().endswith(CONJ) or cmd.strip().endswith(DISJ):
            # remain in reader mode
            pass

        if success: return str(result)
        print('Error: Unable to resolve "%s"; Check the command syntax.' % cmd)

    except Exception as e:
        if DEBUG and USE_PDB: raise
        print('ExecError: ' + str(e))
        return str(None)

def repl(_expr=None, debug=False):
    #if DEBUG: debug = True
    initEnv()
    if USE_HIST in [2, 3] and os.path.exists(HIST_FILE): readline.read_history_file(HIST_FILE)
    global autoclass
    global _tracer

    if not autoclass:
        # first run
        global scp
        scp = importlib.import_module('jnius_config').set_classpath
        exec('scp("%s")' % JAVA_CLASS_PATH.replace(';', '","'), globals())
        autoclass = importlib.import_module('jnius').autoclass
        global cast
        cast = importlib.import_module('jnius').cast
        #if debug: print('DBG: autoclass = %s' % autoclass)
        print(WELCOME_MSG)

    while True:
        if USE_TRACE and not _tracer:
            _tracer = debugging.Trace(ignoremods=['debugging'], ignoredirs=['/usr', '/home/skeledrew/.local'])
        expr = readExpr()
        result = evalExpr(expr) if not USE_TRACE else _tracer.runfunc(evalExpr, expr)
        if result == QUIT: break
        print(result)
    if USE_HIST in [1, 3]: readline.write_history_file(HIST_FILE)
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

def main():
    repl()
    return

if __name__ == '__main__':
    repl()
