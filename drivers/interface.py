"""
    Created by Lawrence Garcia on 1 Feb 2016

"""

import global_vars as gVars
import static_vars as sVars
import simulator
from datatype import BoatData

class Interface:
    """
    This class will interface the simulator with the outside components, either via ZeroMQ or the CAN-Bus.

    """
    def __init__(self, simulated):


        self.name = sVars.CurrentModule

        # Initialize dictionary with everything set to false
        self.simulated = {module: False for module in sVars.AllModules.keys()}

        for module in simulated:
            if module in self.simulated.keys():
                self.simulated[module] = True
            else:
                raise InvalidModuleException('No module "' + str(module) + '" exists. Module skipped.')

        # if (len(simulated) > 0):
        #     gVars.logger.info("Simulated: " + str(gVars.simulated))

        #create the set of modules
        self.modules = set([Module(module, isSimulated) for module, isSimulated in self.simulated.iteritems()])

        self.data = BoatData.BoatData()


    def publish(self, *args):
        """
        :param args: a tuple of parameters to be sent to the bus
        :return: true if successfully sent on bus
        """
        pass

    def getData(self):
        return self.data

    def __str__(self):
        return self.name + " connected to " + str(self.simulated)


class Module:
    def __init__(self, name, simulated=False):
        self.name = name
        self.simulated = simulated

    def getData(self):
        pass

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name


class InvalidModuleException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)
