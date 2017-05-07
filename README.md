# ClIDE

## Description

## Installation

### Requirements
- pexpect (currently unused)
- sh
- pyjnius
- pyparsing
- hylang

## Usage

## Notes
- Python code must use the global scope
- Cannot do Python multiline block statements due to parser operation
- Hy operations are enforced immutable, use as pure functions
- Prolog is meant to manage the knowledge base
- The print function is currently needed to simulate a return
- Cannot use regular parens with parser due to mangling of Python and Prolog functions

## ToDo
- Add Prolog
- Add natural language
- Add initializer
- Add logging
- Line editing and history
- Add JS via Rhino/Nashorn
