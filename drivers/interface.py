"""
    Created by Lawrence Garcia on 1 Feb 2016

"""

# import global_vars as gVars
# import static_vars as sVars
# import simulator
# from datatype import BoatData

import static_vars as sVars
# import global_vars as gVars
from ZMQHandler import ZMQHandler

class Interface:
    """
    This class acts as the interface for the Master Computer to communicate with the outside components.
    The class will be implemented to communicate with the bus, either via ZeroMQ or CAN-Bus.
    """

    def __init__(self, simulated):
        """
        :param simulated: a list of which modules are simulated
        :return:
        """
        self.name = sVars.CurrentModule

        # Create a dictionary with all modules set to False
        self.simulated = {module: False for module in sVars.AllModules.keys()}

        for module in simulated:
            if module in self.simulated.keys():
                self.simulated[module] = True
            else:
                raise InvalidModuleException('No module "' + str(module) + '" exists. Module skipped.')

        if (len(simulated) > 0):
            self.busIsVirtual = True
            self.zmqBus = ZMQHandler()
            # Start reading from the bus
            self.zmqBus.start()

    def publish(self, *args):
        """
        :param args: a tuple of parameters to be sent to the bus
        :return: true if successfully sent on bus
        """
        if self.busIsVirtual:
            return self.zmqBus.write(args)

    def getData(self):
        if self.busIsVirtual:
            return self.zmqBus.data
        else:
            pass
    def getCtrlData(self):
        if self.busIsVirtual:
            return self.zmqBus.control_data
        else:
            pass

    def close(self):
        if self.busIsVirtual:
            self.zmqBus.exitFlag = 1
            self.zmqBus.join()

    def __str__(self):
        return self.name + " connected to " + str(self.simulated) + " by ZeroMQ."


class InvalidModuleException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)