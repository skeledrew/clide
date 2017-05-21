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

import sh, shlex
import pexpect, time
import constants
from utils import clean_ansi
from sh import swipl as plg


class BridgeBase():

    def validate(self, command):
        pass

    def run(self, command):
        pass

class ShellBridge(BridgeBase):

    def __init__(self):
        pass

    def validate(self, command):
        pass

    def run(self, command):
        pass

class PrologBridge(BridgeBase):

    def __init__(self, delay=0.3):
        self._exp_list = [pexpect.EOF, pexpect.TIMEOUT, '\?-', '=']
        self._child = pexpect.spawnu('/bin/bash -c "swipl --quiet --nosignals -s %s"' % constants.KDBASE)
        self._delay = delay
        self._result = ''
        self._plg = swipl.bake('--quiet', '--nosignals', '-s', KDBASE)
        self._aggreg = ''

    def validate(self, command):
        return True

    def run(self, command):
        if not self.validate(command): return False
        log_read = open(constants.TMP_FILE, 'w')
        self._child.logfile_read = log_read
        self._eval_prolog(command)
        log_read.close()
        self._parse_result()
        return self._done_result

    def _eval_prolog(self, cmd):
        asked = False
        answered = False
        self._raw_result = ''
        child = self._child

        while True:
            # interact with the process
            idx = child.expect(self._exp_list)

            if idx == 2 and not asked:
                # at prompt
                child.sendline(cmd)
                asked = True
                continue

            if idx == 2 and asked:
                # at another prompt
                self._raw_result = load_text(constants.TMP_FILE)
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

    def _parse_result(self):
        raw = clean_ansi(self._raw_result)

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
            self._done_result = result
            return

        else:
            # prob shouldn't get here
            print('Why are we here???')
            raise Exception('I really doubt we should be here...')
