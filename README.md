About
=====

Command line interface to change properties of objects with user inputs.

Install
-------

```bash
git clone https://cameleon.univ-lyon1.fr/ovincent/clyo
cd clyo
pip install -e .
```

Install must be done from a git repository (or from PyPI) to get version information.

Quick start
-----------

```python
from clyo import CommandLineInterface
cli = CommandLineInterface(objects, properties, events)
```

See `Example.ipynb` and docstrings of `CommandLineInterface` on how to use.


Misc. info
==========

Testing
-------

Use the `Example.ipynb` notebook.


Python requirements
-------------------

Python >= 3.6

Author
------

Olivier Vincent

(ovinc.py@gmail.com)
