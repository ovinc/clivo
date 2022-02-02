"""Interactive command line interface (CLI)."""


from threading import Event


# TODO -- use match statement with python >= 3.10 instead of if/else


# ================================ MAIN CLASS ================================


class CommandLineInterface:
    """Interactive CLI to manage properties of objects and trigger events

    All objects controlled are referred to with a name.
    Below, we call an arbitrary name X, e.g. X=P for a pressure reading object).

    The CLI can control an arbitrary number of properties for every object
    (for example time interval, averaging number, etc.). These properties
    have commands associated with them.
    Below, we call can arbitrary property command y, e.g. y=dt for time interval.

    It is also possible to trigger events (e.g. request a graph) with some
    pre-defined commands passed as a dict to the CLI class.
    Below, we call these commands for event z

    Once the CLI is started (self.run()), the user input options are:
    - y: inquire current settings (e.g. dt)
    - y val: change property value of all objects to a value val (e.g. dt 10)
    - dt-X val: change settings of only object X to value val (e.g. dt-P 5)
    - z: trigger event (stop event is by default 'Q', 'q' or 'quit', can be changed)
    """

    def __init__(self, objects, properties, events):
        """Create interactive command line interface.

        Parameters
        ----------
        - objects: dict of {name: object} of objects to control
                   (name is a str used in the CLI to refer to the object)
                   objects can define a on_stop() method which indicates
                   specific things to do when the stop event is set.

        - properties: dict of dict describing the properties of the objects
                      that the CLI controls.
                      - The keys are the names of the properties
                        (can be sub-properties, e.g. a property of an attribute)
                      - The values are dicts which must contain the entries
                          - 'repr' (human-readable description for printing)
                          - 'commands': iterable of command names (str) that
                                        will trigger modification of the
                                        property when typed in the CLI

                      Example:
                      {'timer.interval': {'repr': 'Δt (s)',
                                          'commands': ('dt',),
                                          },
                       'averaging': {'repr': 'Averaging',
                                     'commands': ('avg',),
                                     }
                       }

        - events: dict of dict describing the events that the CLI controls.
                  The keys are a description (human-readable) of the event,
                  and the values are dicts which must contain the entries:
                  - 'event': Event object to control (typically, from threading)
                  - 'commands': iterable of command names (str) that
                                will trigger modification of the
                                property when typed in the CLI

                  Example:
                  {'graph': {'event': graph_event,
                             'commands': ('g', 'graph')
                             },
                   'stop': {'event': stop_event,
                            'commands': ('q', 'quit')
                            }
                   }

                   Note: the 'stop' event, if provided, gets linked to the
                   event that triggers exiting of the CLI. If not provided,
                   the 'stop' event is defined internally
        """
        self.objects = objects
        self.properties = properties
        self.events = events

        try:
            self.stop_dict = self.events.pop('stop')
        except KeyError:
            print('Stop event not passed. Creating one internally.')
            self.stop_event = Event()
            self.stop_commands = 'q', 'Q', 'quit'
        else:
            self.stop_event = self.stop_dict['event']
            self.stop_commands = self.stop_dict['commands']

        # Note: stop_commands is a tuple, event/property_commmands are dicts.
        self.event_commands = self._get_commands(self.events)
        self.property_commands = self._get_commands(self.properties)

        # For CLI printing
        self.max_name_length = max([len(obj) for obj in self.objects])

    def _get_commands(self, input_data):
        """Create dict of which command input modifies which property/event.

        Parameters
        ----------
        input_data: dict of dict (can be properties dict or event dict)

        Example
        -------
        input_data = {'graph': {'event': e_graph,
                                'commands': ('g', 'graph')},
                      'stop': {'event': e_stop,
                               'commands': ('q', 'Q', 'quit')}
                      }
        will return {'g': 'graph',
                     'graph': 'graph',
                     'q': 'stop',
                     'Q': 'stop',
                     'quit': 'stop'}
        """
        commands = {}
        for name, data_dict in input_data.items():
            for command_name in data_dict['commands']:
                commands[command_name] = name
        return commands

    def _set_property(self, ppty_cmd, object_name, value):
        """Manage command from CLI to set a property accordingly."""
        obj = self.objects[object_name]
        ppty = self.property_commands[ppty_cmd]
        ppty_repr = self.properties[ppty]['repr']
        try:
            exec(f'obj.{ppty} = {value}')  # avoids having to pass a convert function
        except Exception:
            print(f"'{value}' not a valid {ppty_repr} ({ppty})")
        else:
            print(f'New {ppty_repr} for {object_name}: {value}')

    def _get_property(self, ppty_cmd, object_name):
        """Get property according to given property command from CLI."""
        obj = self.objects[object_name]
        ppty = self.property_commands[ppty_cmd]

        # exec() strategy avoids having to pass a convert function
        self._value = None  # exec won't work with local references
        exec(f'self._value = obj.{ppty}')
        return self._value

    def _print_properties(self, ppty_cmd):
        """Prints current values of properties of all objects"""
        ppty = self.property_commands[ppty_cmd]
        ppty_repr = self.properties[ppty]['repr']

        msgs = [ppty_repr]

        for object_name in self.objects:
            value = self._get_property(ppty_cmd, object_name)
            object_name_str = object_name.ljust(self.max_name_length + 3, '-')
            msg = f'{object_name_str}{value}'
            msgs.append(msg)

        print('\n'.join(msgs))

    # ------------------------------------------------------------------------
    # ========================= MAIN INTERACTIVE CLI =========================
    # ------------------------------------------------------------------------

    def run(self):
        """Start the CLI (blocking)."""

        while not self.stop_event.is_set():

            quit_commands_str = ' or '.join(self.stop_commands)
            command = input(f'Type command (to stop, type {quit_commands_str}): ')

            # Stop all recordings --------------------------------------------

            if command in self.stop_commands:
                print('Stopping recording ...')
                for obj in self.objects.values():
                    try:
                        obj.on_stop()
                    except AttributeError:
                        pass
                self.stop_event.set()

            # Trigger events -------------------------------------------------

            elif command in self.event_commands:
                event_name = self.event_commands[command]
                print(f'{event_name.capitalize()} event requested')
                event = self.events[event_name]['event']
                event.set()

            # Change properties of objects -----------------------------------

            else:

                for ppty_cmd in self.property_commands:

                    nlett = len(ppty_cmd)

                    # e.g. 'dt' --> inquire about current settings ...........
                    if command == ppty_cmd:
                        self._print_properties(ppty_cmd)
                        break

                    # e.g. 'dt 10' --> change setting for all types at once ..
                    elif command[:nlett + 1] == ppty_cmd + ' ':
                        value = command[nlett + 1:]
                        for object_name in self.objects:
                            self._set_property(ppty_cmd, object_name, value)
                        break

                    # e.g. 'dt-P 10' --> change setting only for pressure ....
                    else:
                        found = False
                        for object_name in self.objects:
                            specific_cmd = f'{ppty_cmd}-{object_name}'  # e.g. 'dt-P'
                            nspec = len(specific_cmd)
                            if command[:nspec] == specific_cmd:
                                value = command[nspec + 1:]
                                self._set_property(ppty_cmd, object_name, value)
                                found = True
                                break
                        if found:
                            break

                else:  # at that point, it means nothing else has worked
                    print('Unknown Command. ')
