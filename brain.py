'''

'''

#import constants
import pdb
from pyshell import gen_name, hash_sum


class Mind():

    def __init__(self):
        self._timeline = []
        self._thots = {}

    def register(self, thot):
        self._timeline.append(thot)
        self._thots[thot.t_name] = thot

    def get_thots(self):
        return self._thots

class Thought():

    def __init__(self, mind=None):
        self._done = False
        self._concs = {}
        self._attribs = []
        self._mind = mind if mind else globals()['mind']
        self.t_name = gen_name('thot_', 3, namespace=mind.get_thots())

    def think(self, **kwargs):
        if self._done: return self._results()
        ## do thinking stuff here
        self._kwargs = kwargs

        if kwargs:

            for key in kwargs:
                # set all args as attributes. NB: will overwrite an existing attribute
                if not key == 'attribs': exec('self._%s = kwargs[key]' % key)
                exec('self._attribs.append("_%s")' % key)
        self.t_name = self.t_name.replace('thot', 'thot_%d' % hash_sum(kwargs['content']))
        ## finish up
        self._concs['name'] = self.t_name
        self._concs['kwargs'] = kwargs
        self._dispatch()
        self._done = True
        return self._results()

    def _dispatch(self):
        self._mind.register(self)

    def _links(self):
        pass

    def _results(self):
        return self._concs
