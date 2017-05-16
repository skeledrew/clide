'''

'''


DEBUG = False
MAJOR = 0
MINOR = 1
BUILD = 3
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
