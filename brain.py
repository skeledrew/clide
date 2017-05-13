'''

'''

#import constants
import pdb
from pyshell import gen_name, hash_sum, IFF, CONJ, DISJ, members, read_expr, eval_expr
from fuzzywuzzy import fuzz, process
import inspect


class Mind():
    '''Documentation template for classes and functions.

Longer explanation that may take multiple lines...

:parameters:
  -  `name` (type) - <desc>

:returns: <desc>
:rtype:
(type)
 
:created: 17-05-11
:modified: 17-05-12
:author: Andrew Phillips <skeledrew@gmail.com>
 
.. notes:: <text>
 
.. todo:: <text>
 
.. changes:: <text>
'''

    def __init__(self):
        self._timeline = []
        self._thots = {}
        self._index = {}
        self._word_net = {}

    def register(self, thot):
        self._timeline.append(thot.t_name)
        self._thots[thot.t_name] = thot
        self._index[thot.t_content()] = thot.t_name

    def get_thots(self, chosen=[]):
        # get a list of thoughts, all or opt by name
        thots = {}
        if not chosen: return self._thots

        for t in chosen:
            thots[t] = self._thots[t]
        return thots

    def get_index(self):
        return self._index

    def _ponder(self):
        pass

    def _remember(self):
        pass

    def _imagine(self):
        pass

class Thought():
    '''Documentation template for classes and functions.

Longer explanation that may take multiple lines...

:parameters:
  -  `name` (type) - <desc>

:returns: <desc>
:rtype:
(type)
 
:created: 17-05-11
:modified: 17-05-12
:author: Andrew Phillips <skeledrew@gmail.com>
 
.. notes:: <text>
 
.. todo:: <text>
 
.. changes:: <text>
'''

    def __init__(self, mind=None):
        self._done = False
        self._concs = {}
        self._attribs = []
        self._mind = mind if mind else globals()['mind']
        self.t_name = gen_name('thot_', 3, namespace=mind.get_thots())
        self._act = None
        return

    def _handle_types(self, kwargs):
        c_type = type(kwargs['content'])
        c_types = [type([]), type('')] if not 'c_types' in kwargs else kwargs['c_types']
        if not c_type in c_types: raise Exception('Bad content type.')
        result = None
        if c_type == c_types[0]: result = self._handle_list(kwargs)
        if c_type == c_types[1]: result = self._handle_string(kwargs)
        return result

    def _handle_list(self, kwargs):
        # process a directive
        self._head = self._content.pop(0)[:-3].strip()
        self._body = self._content
        ## do some meta ops with kdb
        return True

    def _handle_string(self, kwargs, max_t=3):
        # process a command
        self._body = None
        self._head = self._content
        m_stats = {}  # matching statistics
        #max_t = 3  # maximum number of top matches
        t_index = self._mind.get_index()
        #t_list = list(t_index)
        content = self._content

        for thot in t_index:
            m_stats[thot] = {}
            m_stats[thot]['ratio'] = fuzz.ratio(content, thot)
            m_stats[thot]['partial_ratio'] = fuzz.partial_ratio(content, thot)
            m_stats[thot]['token_sort_ratio'] = fuzz.token_sort_ratio(content, thot)
            m_stats[thot]['token_set_ratio'] = fuzz.token_set_ratio(content, thot)
        m_stats['top%s' % max_t] = process.extract(content, t_index, limit=max_t)
        self._match_stats = m_stats
        self._pot_acts = m_stats['top%s' % max_t]
        self._act = Action(self, self._pot_acts[0][0])
        result = self._act.do()
        return result

    def think(self, **kwargs):
        if self._done: return self._results()
        ## do thinking stuff here
        if not 'content' in kwargs: raise Exception('No content found.')
        self._kwargs = kwargs

        if kwargs:

            for key in kwargs:
                # set all args as attributes. NB: will overwrite an existing attribute
                if not key == 'attribs': exec('self._%s = kwargs[key]' % key)
                exec('self._attribs.append("_%s")' % key)
        self.t_hash = hash_sum(str(kwargs['content']))  # hash of thought content, string or list
        self.t_name = self.t_name.replace('thot', 'thot_%d' % self.t_hash)
        result = self._handle_types(kwargs)
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

    def t_content(self):
        # return either a sentence or the head as content
        return self._content if not self._body else self._head

class Action():

    def __init__(self, thot, targ_thot_name):
        self._thot = thot
        targ_thot = thot._mind.get_thots([targ_thot_name])[targ_thot_name]
        self._conc = targ_thot.think()
        self._body = self._conc['kwargs']['content']  # body of a directive
        self._command = thot._head  # current command
        self._head = targ_thot._head  # head of a directive

    def store(self):
        pass

    def do(self):
        # execute the commands
        body = self._body
        head = self._head
        result = None
        partial = None

        for cmd in body:

            if cmd.endswith(CONJ):
                # stop processing commands if nothing was returned
                partial = eval_expr(read_expr(cmd[:-3]))
                if partial == None: break
                continue

            elif cmd.endswith(DISJ):
                # stop processing when something is returned
                partial = eval_expr(read_expr(cmd[:-3]))
                if not partial == None: break
                continue

            else:
                # last command in the body
                partial = eval_expr(read_expr(cmd))
        result = partial
        return result
