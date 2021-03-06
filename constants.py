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


DEBUG = False
MAJOR = 0
MINOR = 1
BUILD = 8
OB = '<{'
CB = '}>'
QUIT = 'quit...'
PROMPT = '_'
JAVA_CLASS_PATH = '.;/home/skeledrew/Projects/htmlunit/2.26/lib/*'
INIT_FILE = 'clide.init'
WELCOME_MSG = 'Welcome to ClIDE, the Command-line IDE v%d.%d.%d\n' % (MAJOR, MINOR, BUILD)
COMMENT = '#'
INITD = False  # True if initialization file was successfully read
KDBASE = 'clide.pl'
USE_PDB = False
TMP_FILE = 'clide.tmp'
HIST_FILE = 'clide.hist'
USE_HIST = 3  # 0 = none, 1 = save, 2 = load, 3 = all
IFF = ':=>'  # separate pseudolog head and body
CONJ = '&&&'  # conjunct 2 body parts
DISJ = '|||'  # disjunct 2 body parts
ALPHA_LOWER = ''.join([chr(i) for i in range(97, 123)])
ALPHA_UPPER = ''.join([chr(i) for i in range(65, 91)])
NUMBERS = ''.join([str(i) for i in range(0, 10)])
USE_TRACE = False
EXIT_MSG = 'Goodbye cruel world :\'('
EARS_LISTENING = 'I\'m all ears...'
EARS_UNDERSTANDING = 'Trying to understand what was said!'
LUAL_QUIT = 'finish'
ACCEPTED = ALPHA_LOWER + ALPHA_UPPER + ' '
MEMORY_PATH = 'memories/'
NO_POT_ACT = 'I am unable to answer to "%s". Can you teach me?'
BAD_POT_ACT = 'I thought I understood that, but I didn\'t...'
MEMORY = True
USE_MARY_TTS = True
MARY_TTS_PATH = '/home/skeledrew/Projects/MaryTTS/marytts-installer-5.2/'
SPOKEN_WORDS_PATH = 'spoken_words/'
DEFAULT_MARY_VOICE = 'cmu-slt-hsmm'
LAST_RESULT = 'LastResult'
UNIFY_ERROR = 'Cannot unify; "%s" is already resolved'
CURRENT_COMMAND = 'CurrentCommand'
