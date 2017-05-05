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


def main():
    while True:
        cmd = input('<= ')
        if cmd == 'goodbye': break

        try:
            exec(cmd)

        except:
            print('exec failed')
if __name__ == '__main__':
    main()
