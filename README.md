## ClIDE -- Command-line Intelligent Development Environment

### Description
ClIDE is essentially a multi-language interpreter that can interface with different languages including
Hy, Shell, Java and even natural (yes, it can handle NL sentences with a little assistance!). The final aim is an interpreter that can learn and act upon statements, commands and queries given in natural language. Action scope go from on the desktop to internet, etc. This will make it easier not only to develop apps, but to use computer resources in a more natural way.

### Installation
- Install requirements (soon to be automated)
- Edit JAVA_HOME in 'clide' to point to your install
- Make executable with 'chmod +x clide'
- Create an init file 'clide.init'
- Run ./clide
- Experiment!

#### Requirements
- java
- swi-prolog
- python3
- libdbus-glib-1-dev (for autohotkey)
- ---
- pexpect
- sh (for Shell access)
- pyjnius (for Java access)
- pyparsing
- hy (for Hy access)
- pyswip (for Prolog access)
- fuzzywuzzy[speedup]
- pynput
- autokey
- probably more...

### Usage
- Enter 'quit...' to quit
- Prepend Shell commands with '$'
  - '$ ls -lt'
- Prepend Python commands with '>'
  - '> global myvar; myvar = 13'
- Hy commands must be in a single parens
  - '(+ 5 12)'
- Access Java classes from Python
  - '> j_import("java.lang.System")'
  - '> System.out.println("Hello from Java!")'
- Add interesting classpaths to the init file (cannot be done at the repl)
  - '> JAVA_CLASS_PATH += ";/path/to/jar/files/*;/more/paths/*"' (note the extra quotes)
- Nest multiple langs with '<{' and '}>'
  - '> myvar = <{(/ 100 31)}>
- Access Prolog from Python (via pyswip)
  - '> prolog = Prolog(); prolog.assertz("father(michael,john)")'
- Prepend pure Prolog commands with '?' or end with '.'
  - 'human(socrates).'
- Append ' :=>' to a sentence/phrase to start a directive (note the space)
  - 'tell time :=>'
- Append ' &&&' (for logical and) or ' |||' (for logical or) to sentences/commands in a directive
- A directive is completed when non of the latter 2 postfixes are used
  - '> import time &&&'
  - '> print(time.time())'
- Run a directive by giving a sentence/phrase. The best matching stored directive will be sought
  - 'tell me the time'
- Report errors (I'm sure there are many :))

### Notes
- Python code must use the global scope
- Cannot do Python multiline block statements due to parser operation
- Hy operations are enforced immutable,use as pure functions
- Prolog is meant to manage the knowledge base
- The print function is currently needed to simulate a return for Python statements and Hy
- Cannot use regular parens with parser due to mangling of Python and Prolog functions
- Prolog works for unknown reasons; may break any time
- The global variables '_last_shell_result' and '_last_shell_result' can be used for issues with using nested Shell and Prolog

### ToDo
- Add natural language
- Add logging
- Add JS via Rhino/Nashorn
- Setup script
- Autodetect lang without identifier use

### Doc Template
'''Documentation template for classes and functions.

Longer explanation that may take multiple lines...

:parameters:
  -  `name` (type) - <desc>

:returns: <desc>
:rtype:
(type)
 
:created: 17-05-11
:modified: 17-05-11
:author: Andrew Phillips <skeledrew@gmail.com>
 
.. notes:: <text>
 
.. todo:: <text>
 
.. changes:: <text>
'''

NB: If multiple types, put types in curlies.