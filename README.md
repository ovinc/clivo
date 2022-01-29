About
=====

Command line interface to change properties of objects in real time.

Install
-------

```bash
git clone https://cameleon.univ-lyon1.fr/ovincent/clyo
cd clyo
pip install -e .
```

Install must be done from a git repository, because version information is extracted automatically from the git commits when saving metadata.

Configure
---------

The properties that the CLI has to monitor modify need do be defined as subclasses of the `Property` abstract base class. The subclass must define:
- `ptype`: identifier of property of interest (e.g. 'dt' for time interval)
- `name`: corresponding human-readable name for printing
- `convert_input()`: how to convert command line input to useful property value
- `on_stop()`: define what happens when a stop request comes from the CLI
- `value`: a settable attribute (property): that indicates how to set and get the value associated with the property type of interest


Misc. info
==========


Python requirements
-------------------

Python >= 3.6

Author
------

Olivier Vincent

(ovinc.py@gmail.com)
