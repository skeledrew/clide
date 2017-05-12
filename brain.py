'''

'''

#import constants
from zlib import adler32 as hash_sum  # returns an int


class Mind():

    def __init__(self):
        global mind

        if mind:
            # single mind
            del self
            return
        exec('mind = self')
        self._timeline = []
        self._thots = {}

    def register(self, thot):
        self.timeline.append(thot)
        self._thots[thot[t_name]] = thot

    def get_thots(self):
        return _thots

class Thought():

    def __init__(self, mind=None):
        self._done = False
        self._concs = {}
        self._attribs = []
        self._mind = mind if mind else globals()['mind']
        self.t_name = gen_name('thot-', 3, namespace=mind.get_thots())

    def think(self, **kwargs):
        if self._done: return self._results()
        ## do thinking stuff here
        self._kwargs = kwargs

        if kwargs:

            for key in kwargs:
                # set all args as attributes. NB: will overwrite an existing attribute
                if not key == 'attribs': exec('self._%s = kwargs[key]' % key)
                exec('self._attribs.append("_%s")' % key)
        self.t_name = self.t_name.replace('thot', 'thot-%d' % hash_sum(kwargs['content']))
        ## finish up
        self._dispatch()
        self._done = True
        return self._results()

    def _dispatch(self):
        self.mind.register(self)

    def _links(self):
        pass

    def _results(self):
        return _concs
