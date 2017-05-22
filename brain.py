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


import pdb
from pyshell import read_expr, eval_expr
from fuzzywuzzy import fuzz, process
import inspect
from utils import gen_name, hash_sum, members, save_pickle, load_pickle
import os, time
import constants


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

    def __init__(self, persist=True, name='main_mind'):
        self._timeline = []
        self._thots = {}
        self._index = {}
        self._word_net = {}
        if persist and os.path.exists(constants.MEMORY_PATH): self._recall(name)
        if persist and not os.path.exists(constants.MEMORY_PATH): os.makedirs(constants.MEMORY_PATH)
        self._persist = persist
        self._name = name

    def register(self, thot):
        self._timeline.append(thot.t_name)
        self._thots[thot.t_name] = thot
        self._index[thot.t_content()] = thot.t_name
        self._commit(thot)

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

    def _remember(self, t_names):
        if self._persist: return [load_pickle('%s%s.obj' % (constants.MEMORY_PATH, t_name)) for t_name in t_names]

    def _imagine(self):
        pass

    def _commit(self, thot=None):
        if self._persist and thot: save_pickle(thot, '%s%s.obj' % (constants.MEMORY_PATH, thot.t_name))
        if self._persist and not thot: save_pickle(self, '%s%s.obj' % (constants.MEMORY_PATH, self._name))
        return

    def _recall(self, name):
        # init with stored mind
        mind = load_pickle('%s%s.obj' % (constants.MEMORY_PATH, name))

        if mind:
            self._timeline = mind._timeline
            self._thots = mind._thots
            self._index = mind._index
            self._word_net = mind._word_net
        return

    def save(self):
        self._commit()

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

    def __init__(self, mind=None, persist=True):
        self._done = False
        self._concs = {}
        self._attribs = []
        self._mind = mind if mind else globals()['mind']
        self._act = None
        return

    def _handle_types(self, kwargs):
        c_type = type(kwargs['content'])
        c_types = [list, str] if not 'c_types' in kwargs else kwargs['c_types']
        if not c_type in c_types: raise Exception('Bad content type.')
        result = None
        if c_type == list: result = self._handle_list(kwargs)
        if c_type == str: result = self._handle_string(kwargs)
        return result

    def _handle_list(self, kwargs):
        # process a directive
        self._head = self._content.pop(0)[:-3].strip()
        self._body = self._content
        self._needsUnify = False

        for word in self._head.split(' '):

            if ord(word[0]) in range(65, 91):
                self._needsUnify = True
                break
        ## do some meta ops with kdb
        return 'I just learned something new!'

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
        if not self._pot_acts: return constants.NO_POT_ACT % content
        # FIXME: [1] need to check for a viable resolver, or maybe discard the thought
        choice = ''

        for c in self._pot_acts:
            # find a suitable though with an action

            '''if c[0][:-3] == self.t_name[:-3]:
                # identical thought; skip it (for now?)
                continue'''
            pot_targ_thot = self._mind.get_thots([c[0]])[c[0]]

            if not type(pot_targ_thot.think()['kwargs']['content']) == list:
                # doesn't have actionable content
                continue
            # add other undesirable checks
            choice = c[0]
        if not choice: return constants.NO_POT_ACT % content
        self._act = Action(self, choice)
        result = self._act.do()
        return result

    def think(self, **kwargs):
        if self._done: return self._results()
        if not 'content' in kwargs: raise Exception('No content found.')
        self._t_start = time.time()
        self._kwargs = kwargs

        if kwargs:

            for key in kwargs:
                # set all args as attributes. NB: will overwrite an existing attribute
                if not key == 'attribs': exec('self._%s = kwargs[key]' % key)
                exec('self._attribs.append("_%s")' % key)
        self.t_hash = hash_sum(str(kwargs['content']))  # hash of thought content, string or list
        self.t_name = gen_name('thot_%d_' % self.t_hash, 3, namespace=self._mind.get_thots())
        #self.t_name = self.t_name.replace('thot', 'thot_%d' % self.t_hash)
        result = self._handle_types(kwargs)
        ## finish up
        self._concs['name'] = self.t_name
        self._concs['kwargs'] = kwargs
        self._done = True
        self._t_end = time.time()
        self._dispatch()
        return result

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

        if not type(self._body) == list:
            # no action available; prob obselete
            self._body = None
        self._command = thot._head  # current command
        self._head = targ_thot._head  # head of a directive

    def store(self):
        pass

    def do(self):
        # execute the commands
        body = self._body
        if not body:
            # should be obselete
            print(constants.BAT_POT_ACT)
            return None
        head = self._head
        result = None
        partial = None

        for cmd in body:

            if cmd.endswith(constants.CONJ):
                # stop processing commands if nothing was returned
                partial = eval_expr(read_expr(cmd[:-3]))
                if partial == None: break
                continue

            elif cmd.endswith(constants.DISJ):
                # stop processing when something is returned
                partial = eval_expr(read_expr(cmd[:-3]))
                if not partial == None: break
                continue

            else:
                # last command in the body
                partial = eval_expr(read_expr(cmd))
        result = partial
        return result
