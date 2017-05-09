## ClIDE -- Command-line Integrated Development Environment

### Description
ClIDE is essentially a Python interpreter that mixes different languages, including
Hy, Shell, Java and eventually Prolog, JavaScript and natural! The final aim is
an interpreter that can take natural language and learn as well as perform actions
on the desktop, internet, etc.

### Installation
- Install requirements (soon to be automated)
- Edit JAVA_HOME in 'clide' to point to your install
- Make executable with 'chmod +x clide'
- Create an init file 'clide.init'
- Run ./clide
- Experiment!

#### Requirements
- python3
- pexpect
- sh
- java
- pyjnius
- pyparsing
- hy
- swi-prolog
- pyswip
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
 - '> global System; System = autoclass("java.lang.System")'
 - '> System.out.println("Hello from Java!")'
- Add interesting classpaths to the init file (cannot be done at the repl)
 - '> JAVA_CLASS_PATH += ";/path/to/jar/files/*;/more/paths/*"' (note the extra quotes)
- Nest multiple langs with '<{' and '}>'
 - '> myvar = <{(/ 100 31)}>
- Access Prolog from Python (via pyswip)
 - '> prolog = Prolog(); prolog.assertz("father(michael,john)")'
- Prepend pure Prolog commands with '?' or end with '.'
 - 'human(socrates).'
- Report errors (I'm sure there are many :))

### Notes
- Python code must use the global scope
- Cannot do Python multiline block statements due to parser operation
- Hy operations are enforced immutable, use as pure functions
- Prolog is meant to manage the knowledge base
- The print function is currently needed to simulate a return for Python statements and Hy
- Cannot use regular parens with parser due to mangling of Python and Prolog functions
- Prolog works for unknown reasons; will break any time

### ToDo
- Add natural language
- Add logging
- Line editing and history
- Add JS via Rhino/Nashorn
- Setup script
- Autodetect lang without identifier use
