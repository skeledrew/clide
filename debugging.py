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

import trace
import linecache


class Trace(trace.Trace):
    watchlist = {}

    def add_watch(self, *vars):
        for var in vars:
            if not var in self.watchlist: self.watchlist[var] = None
            print('Added "%s" to the watchlist' % var)
        return

    def pop_watch(self, var):
        if var in self.watchlist: print('Removed "%s" from the watchlist' % var)
        return self.watchlist.pop(var, None)

    def get_watchlist(self):
        list_ = [var for var in self.watchlist]
        print('Watchlist contains: %s' % ' '.join(list_))
        return list_

    def del_watchlist(self):
        self.watchlist = {}
        return

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def check_watchlist(self, frame):
        filename = frame.f_code.co_filename
        lineno = frame.f_lineno
        line = linecache.getline(filename, lineno)
        funcname = frame.f_code.co_name

        if self.watchlist:
            frame_vars = frame.f_locals

            for var in self.watchlist:
                func = '*'

                if '-' in var:
                    # separate specific function
                    func = var.split('-')[0]
                    var = var.split('-')[1]

                if var in line and var in frame_vars and (func == funcname or func == '*'):
                    # crude way to find if a var is about to be accessed
                    print(' -- in %s, %s = "%s"' % (funcname, var, str(frame_vars[var])))

    def localtrace_trace_and_count(self, frame, why, arg):
        result = super().localtrace_trace_and_count(frame, why, arg)
        self.check_watchlist(frame)
        return result

    def localtrace_trace(self, frame, why, arg):
        result = super().localtrace_trace(frame, why, arg)
        self.check_watchlist(frame)
        return result
