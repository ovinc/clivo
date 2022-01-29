"""Interactive command line interface."""


from abc import ABC, abstractmethod


# TODO -- use match statement with python >= 3.10 instead of if/else


class Property(ABC):
    """Abstract base class identifying which attributes/methods properties have.
    """

    @abstractmethod
    def convert_input(self, cmd):
        """how to convert command line input to useful property value"""
        pass

    @abstractmethod
    def on_stop(self):
        """define what happens when a stop request comes from the CLI"""
        pass

    # Below, these attributes can be implemented as class attributes ---------

    @property
    @abstractmethod
    def ptype(self):
        """identifier of property of interest (e.g. 'dt' for time interval)"""
        pass

    @property
    @abstractmethod
    def name(self):
        """corresponding human-readable name for printing"""
        pass

    # Settable value property ------------------------------------------------

    @property
    @abstractmethod
    def value(self):
        pass

    @value.setter
    @abstractmethod
    def value(self, val):
        pass


# ================================ MAIN CLASS ================================


class CommandLineInterface(ABC):
    """Interactive Command Line class to manage time interval in recordings etc.

    For use in threaded environements with recording of several sensors.
    In this help, we call an arbitrary sensor X, e.g. X=P for pressure).

    The CLI can control an arbitrary of settings (properties) for every sensor
    recording, e.g. time interval.
    In this help, we call can arbitrary property y, e.g. y=dt for time interval.

    Once the CLI is started (self.run()), the user input options are:
    - q or Q: (exit)
    - g or graph: (pop up live graph of data)
    - y: inquire current settings (e.g. dt)
    - y val: change settings of all recordings to a value val (e.g. dt 10)
    - dtX val: change settings of only sensor X to value val (e.g. dtP 5)
    """

    def __init__(self, properties, e_graph, e_stop):
        """Create interactive command line interface.

        Parameters
        ----------
        - properties: object or objects that the ppties defined in the
          config above are supposed to act upon. define in init_ppties above
          what these objects should be and how to process them.

        - e_graph: threading event requesting a live graph of the data.

        - e_stop: threading event signaling recording to stop
        """
        self.ppties = self.init_ppties(properties)  # dict of dicts, keys ppty

        self.e_stop = e_stop
        self.e_graph = e_graph

    @staticmethod
    @abstractmethod
    def init_ppties(properties):
        """Define how to to manage the received properties

        Must return a dict of dicts with keys:
          - property identifiers (ptype) as defined above, e.g. 'dt'
          - names (names of sensors/devices etc. managed by the CLI)
        and with the individual property objects defined above as values.

        Example
        -------
        # objects needed as parameters to instantiate the classes above
        timers, avgnums = properties
        names = timers.keys()  # both timers and avgnums should have the same keys

        # instanciate the classes above and put them in a dictionary with sensor
        # names as keys
        time_intervals = {name: TimeInterval(timers[name]) for name in names}
        avg_numbers = {name: AveragingNumber(timers[name], avgnums[name]) for name in names}

        return {'dt': time_intervals, 'avg': avg_numbers}
        """
        pass

    def set_property(self, ptype, name, command):
        """manage command from CLI to set a property accordingly."""
        try:
            ppty = self.ppties[ptype][name]
        except KeyError:
            msg = f'Unknown property type ({ptype}) or data name ({name})'
            raise ValueError(msg)

        try:
            ppty.value = ppty.convert_input(command)
        except Exception:
            print(f"'{command}' not a valid {ppty.name}")
        else:
            print(f'New {ppty.name} for {name}: {ppty.value}')

    def print_properties(self, ptype):
        """Prints current values of properties (dt / avg)"""
        msgs = []
        for name, ppty in self.ppties[ptype].items():
            msg = f' {ppty.name} [{name}] = {ppty.value}'
            msgs.append(msg)
        print(', '.join(msgs))

    # ------------------------------------------------------------------------
    # ========================= MAIN INTERACTIVE CLI =========================
    # ------------------------------------------------------------------------

    def run(self):
        """Command Line Interface for interactive control during recording."""

        while not self.e_stop.is_set():

            command = input("Type command (Q to stop recording) : ")

            # Stop all recordings ('Q' or 'q') -------------------------------

            if command == 'q' or command == 'Q':
                print('Stopping recording ...')
                for ppties in self.ppties.values():
                    for ppty in ppties.values():
                        ppty.on_stop()
                self.e_stop.set()

            # Request a live graph of the data -------------------------------

            elif command == 'graph' or command == 'g':
                self.e_graph.set()

            # Change the time intervals or avg of data recording -------------

            else:

                for ptype, ppties in self.ppties.items():  # ptype is 'dt' or 'avg'

                    nlett = len(ptype)

                    # e.g. 'dt' --> inquire about current settings ...........
                    if command == ptype:
                        self.print_properties(ptype)
                        break

                    # e.g. 'dt 10' --> change setting for all types at once ..
                    elif command[:nlett + 1] == ptype + ' ':
                        for name in ppties:  # name is e.g. 'P', 'T', etc.
                            self.set_property(ptype, name, command[nlett + 1:])
                        break

                    # e.g. 'dtP 10' --> change setting only for pressure .....
                    else:
                        found = False
                        for name in ppties:
                            specific_cmd = ptype + name  # e.g. 'dtP'
                            nspec = len(specific_cmd)
                            if command[:nspec] == specific_cmd:
                                self.set_property(ptype, name, command[nspec + 1:])
                                found = True
                                break
                        if found:
                            break

                else:  # at that point, it means nothing else has worked
                    print('Unknown Command. ')
