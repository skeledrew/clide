#! /usr/bin/python3


'''
PyShell
- A thin Python REPL providing additional functions
- Addons:
-- Session save/autosave/load
-- Input history
-- Output logging
-- Init templates
-- Allow multiline code correction and formatting
'''


#from common import *
import pexpect
import sys
import importlib, inspect
import sh, shlex


DEBUG = False
MAJOR = 0
MINOR = 1
autoclass = None
cast = None


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
    #raise Exception('Something went wrong in pesh')

def launch(cmd, shell='/bin/bash'):
    child = pexpect.spawnu(shell, ['-c', cmd] if type(cmd) == type('') else cmd, timeout=None)
    child.expect([pexpect.EOF, pexpect.TIMEOUT])

def repl(debug=False):
    if DEBUG: debug = True
    #pysh('export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64')
    scp = importlib.import_module('jnius_config').set_classpath
    scp('.')
    global autoclass
    autoclass = importlib.import_module('jnius').autoclass
    global cast
    cast = importlib.import_module('jnius').cast
    if debug: print('DBG: autoclass = %s' % autoclass)
    print('Welcome to ClIDE, the Command-line IDE v%d.%d (---)\n' % (MAJOR, MINOR))

    while True:
        cmd = input('_')
        if cmd == 'quit...': break
        result = None

        try:

            if cmd[0] == '>':
                # execute as Python
                exec(cmd[1:].strip())
                result = 1
                continue

            if not result and cmd[0] == '(':
                # execute as Hy
                result = sh.hy('-c', cmd)
                print(result)
                continue


            if cmd[0] == '$':
                # execute as Shell
                result = pysh(cmd[1:].strip())
                print(result)
                continue

            print('Error: Unable to resolve "%s"; Check the command syntax.' % cmd)

        except Exception as e:
            print('ExecError: ' + str(e))
        #print(result)

if __name__ == '__main__':
    repl()
