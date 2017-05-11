'''

'''

import trace
import functools
import linecache


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

                if '.' in var:
                    # separate specific function
                    func = var.split('.')[0]
                    var = var.split('.')[1]

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
