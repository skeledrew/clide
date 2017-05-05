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

def main():
    while True:
        cmd = input('<= ')
        if cmd == 'goodbye': break

        try:
            exec(cmd)

        except:
            pesh(cmd)
if __name__ == '__main__':
    main()
