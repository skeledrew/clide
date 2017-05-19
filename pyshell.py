#! /usr/bin/python3

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
import sh, shlex
from pyparsing import nestedExpr
import pdb
import os
from pyswip import *
from io import StringIO
import time
import debugging
from hy.cmdline import run_command as run_hy
from contextlib import redirect_stdout
from constants import *
from utils import *
from fingers import Finger
from ears import Ear
from hy_hooks import HyBridge, HyREPL, run_repl
import constants


autoclass = None
cast = None
_last_shell_result = None
_last_prolog_result = None
_tracer = None
mind = None
_multiline = False
prolog = None


def eval_prolog_with_pyswip(cmd):
    # use the pyswip methods for evaluation
    #   faster and cleaner, but less flexible
    global prolog
    if not prolog: prolog = Prolog()
    result = None
    cmd = cmd.strip()  # make it easier to search
    if cmd[-1] == '.': cmd = cmd[:-1]  # remove the period
    #cmd = cmd[:-1] + '.)'  # insert a period befor last parens

    if cmd.startswith('asserta'):
        assn = cmd[8:-1]
        result = prolog.asserta(cmd)

    elif cmd.startswith('assertz'):
        assn = cmd[8:-1]
        result = prolog.assertz(cmd)

    elif cmd.startswith('retract'):
        assn = cmd[8:-1]
        result = prolog.retract(cmd)

    elif cmd.startswith('retractall'):
        assn = cmd[11:-1]
        result = prolog.retractall(cmd)

    elif cmd.startswith('dynamic'):
        #cmd = cmd[:-2] + ')'
        assn = cmd[8:-1]
        result = prolog.dynamic(cmd)

    elif cmd.startswith('consult'):
        assn = cmd[8:-1]
        result = prolog.consult(cmd)

    else:
        #assn = cmd[6:-1]
        result = prolog.query(cmd)
    return 'true.' if result == {} else 'false.' if result == None else result

def eval_pseudolog(cmd):
    global mind
    if not mind: mind = Mind() #if Mind else load_module('brain').Mind()
    result = Thought(mind).think(content=cmd)
    return result

def eval_prolog_with_pexpect(cmd):
    if DEBUG: debug = True
    expList = [pexpect.EOF, pexpect.TIMEOUT, '\?-', '=']
    child = pexpect.spawnu('/bin/bash -c "swipl --quiet --nosignals -s %s"' % KDBASE)
    child.logfile_read = open(TMP_FILE, 'w')
    asked = False
    answered = False
    raw = ''

    while True:
        # interact with the process
        idx = child.expect(expList)
        time.sleep(0.5)

        if idx == 2 and not asked:
            # at prompt
            child.sendline(cmd)
            asked = True
            continue

        if idx == 2 and asked:
            # at another prompt
            raw = load_text(TMP_FILE)
            break

        if idx == 13:
            # prob got all the result. NB: should be #3 targetting '.' but currently works w/out
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

    if True:
            # TODO: decrease indents and remove useless if
            raw = clean_ansi(raw)

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
                        # binding; TODO: upgrade to intelligent detection
                        line = line.split(' = ')
                        if line[1][-1] == ';' or line[1][-1] == '.': line[1] = line[1][:-1].strip()
                        rare.append({line[0]: line[1]})

                    else:
                        # other returns
                        rare.append(line.strip())
                result = rare if len(rare) > 1 else rare[0]  # return list or single
                return result

            else:
                # prob shouldn't get here
                print('Why are we here???')
                raise Exception('I really doubt we should be here...')

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

def read_expr(cmd='', debug=False):
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

def process_expr(expr, cmd=''):
    if isinstance(expr, str): return expr

    for item in expr:
        # process each list element at the current level
        #if debug: print('DBG: item = %s' % item)

        if isinstance(item, list):
            # process a nested list
            #if debug: print('DBG: level = %d' % level)
            cmd += eval_expr(item, level=level+1) + ' '

        else:
            cmd += item + ' '
    return cmd

def eval_expr(_expr=None, level=0, debug=False):
    # Recursively evaluates expression as a - nested - list of strings
    expr = None if _expr == None else _expr[:]  # prevent recursive reference hell
    if not expr: return None  # short circuit no input
    global _multiline
    cmd = process_expr(expr) #if not multiline else expr
    cmd = cmd.strip()
    if level == 0 and cmd == QUIT: return QUIT
    result = None
    success = False
    accepted = constants.ACCEPTED
    if constants.USE_PDB: pdb.set_trace()

    try:

        if cmd.endswith(CONJ) or cmd.endswith(DISJ):
            # remain in multiline reader mode

            if _multiline:
                #_lines.append(cmd)
                return cmd
                success = True

            else:
                raise Exception('Expected preceding head sentence denoted by %s' % IFF)

        if _multiline and not (cmd.endswith(CONJ) or cmd.endswith(DISJ)):
            # read last line
            #result = _lines.append(cmd)
            _multiline = False
            return cmd
            success = True

        if cmd.startswith(OB) and cmd.endswith(CB):
            # top level enclosure
            pass

        if not success and cmd[0] == '>':
            # execute as Python

            try:
                result = eval(cmd[1:].strip(), globals())
                #if not result: result = True

            except:
                sio = StringIO()

                with redirect_stdout(sio):
                    exec(cmd[1:].strip(), globals())
                result = sio.getvalue()
            success = True

        if not success and cmd[0] == '(':
            # execute as Hy
            #if cmd[1] in '>$?': return cmd  # not to be eval'd with Hy
            if not 'print' in cmd: cmd = '(print %s)' % cmd  # wrap with print to trigger return
            #result = sh.hy('-c', cmd)
            sio = StringIO()

            with redirect_stdout(sio):
                run_hy(cmd)
            result = sio.getvalue()
            success = True

        if not success and cmd[0] == '$':
            # execute as Shell
            result = pysh(cmd[1:].strip())
            global _last_shell_result
            _last_shell_result = result
            #result = '"%s"' % result  # should fix embedded issue
            #if debug: print('DBG: shell result = %s' % result)
            success = True

        if not success and cmd[0] == '?' or cmd[-1] == '.':
            # execute as Prolog; yields a boolean, string or list of bindings
            if cmd[0] == '?': cmd = cmd[1:].strip()
            if not cmd[-1] == '.': cmd += '.'
            #result = pesh('swipl -s %s -g "%s" -t halt' % (KDBASE, cmd), 0)
            result = eval_prolog_with_pexpect(cmd)
            global _last_prolog_result
            _last_prolog_result = result
            success = True

        if not _multiline and cmd.endswith(IFF):
            # activate multiline reader mode for pseudolog directive

            for char in cmd[:-3]:
                # ensure all chars are valid

                if not char in accepted:
                    raise Exception('Invalid character detected. Command should only include "%s"' % accepted)
            lines = [cmd]
            _multiline = True

            while _multiline:
                # inner repl
                line = eval_expr(read_expr())
                lines.append(line)
            #lines = ' '.join(lines)
            result = eval_pseudolog(lines)
            success = True

        if not success:
            # should be natural language
            isAcceptable = False

            for char in cmd:

                if not char in accepted:
                    isAcceptable = False
                    break
                isAcceptable = True

            if isAcceptable:
                result = eval_pseudolog(cmd)
                success = True

        if success: return str(result)
        print('Error: Unable to resolve "%s"; Check the command syntax.' % cmd)

    except Exception as e:
        print('ExecError: ' + str(e))
        print('Activating pdb for post-mortem debugging...\n')
        pdb.post_mortem()
        return None

def repl(_expr=None, debug=False):
    global Mind, Thought, Action, mind
    Mind = load_module('brain').Mind
    Thought = load_module('brain').Thought
    Action = load_module('brain').Action
    mind = Mind()
    init_env()
    if USE_HIST in [2, 3] and os.path.exists(HIST_FILE): readline.read_history_file(HIST_FILE)
    global autoclass
    global _tracer

    print(WELCOME_MSG)

    while True:
        if USE_TRACE and not _tracer:
            _tracer = debugging.Trace(ignoremods=['debugging', 'utils'], ignoredirs=['/usr', '/home/skeledrew/.local'])
        expr = read_expr()
        result = eval_expr(expr) if not USE_TRACE else _tracer.runfunc(eval_expr, expr)
        if result == QUIT: break
        print(result)
    if USE_HIST in [1, 3]: readline.write_history_file(HIST_FILE)
    print('Goodbye cruel world :\'(')

def init_env():
    # Initialize the environment with commands from a file
    readline.set_completer(HistoryCompleter().complete)
    readline.parse_and_bind('tab: complete')
    readline.parse_and_bind('set enable-keypad on')

    if not os.path.isfile(INIT_FILE): return

    with open(INIT_FILE) as fo:

        for line in fo:
            cmd = read_expr(line)
            if cmd: eval_expr(cmd)
    return

def main():
    run_repl(read_expr, eval_expr)
    return

if __name__ == '__main__':
    #main()
    repl()
