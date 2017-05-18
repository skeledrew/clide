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


import hy.cmdline as hy_line
import pdb
from debugging import Trace
import constants
import sys


class HyBridge():

    def __init__(self, spy, namespace):
        hr = hy_line.HyREPL(spy, namespace)
        setattr(hr, '_runsource', hr.runsource)
        setattr(hr, 'runsource', self.runsource)
        self.locals = hr.locals
        self._hr = hr

    def run(source, spy=False):
        self._hr.runsource(source)

    def runsource(source, filename='<input>', symbol='single'):
        print('about to call runsource')
        self._hr._runsource(source, filename, symbol)
        print('done with runsource')
        return 0

class HyREPL(hy_line.HyREPL):

    def __init__(self, readfunc, evalfunc, spy=False, namespace={}):
        self._readfunc = readfunc
        self._evalfunc = evalfunc
        super().__init__(spy, namespace)

    def runsource(self, source, filename='<input>', symbol='single'):
        cmd = self._readfunc(source)

    def _runsource(self, source, filename='<input>', symbol='single'):
        super().runsource(source, filename, symbol)

def run_repl(readfunc=None, evalfunc=None, local=None):
    tracer = Trace(ignoremods=['debugging'])
    spy = False
    sys.ps1 = constants.PROMPT
    sys.ps2 = '... '
    namespace = globals()
    print('hy starting...')
    hy_line.HyREPL = HyREPL
    pdb.set_trace()
    hr = HyREPL(readfunc, evalfunc, spy, namespace)
    #setattr(hr, '_runsource', hr.runsource)
    #setattr(hr, 'runsource', runsource)
    hr.runsource('(setv myvar (+ 5 8))')
    print('myvar result is ', hr.locals['myvar'])
    hr.interact(constants.WELCOME_MSG)  # TODO: upgrade to python 3.6 for extended method
    print('hy done!')

def runsource(self, source, filename='<input>', symbol='single'):
    print('about to call runsource')
    self._runsource(source, filename, symbol)
    print('done with runsource')
    return 0
