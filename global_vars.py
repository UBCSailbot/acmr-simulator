"""
Created on 2 Feb 2016

Global Variables for the control logic
-   All variables set by main in the control logic are stored in the
    global variable class.  Global variables can be accessed from other
    classes, however, they are not set outside of main.py or simulator.py

"""
import datatype



# list of all simulated components
simulated = set()
# functionQueue = []
# queueParameters = []
# boundaries = []

boatVars = datatype.BoatData.BoatData()
interfaceData = None

run = True
currentProcess = None
currentParams = None
taskStartTime = None
currentColumn = 0
verbose = False
reset = False
gust = False
dataToUI = False

bus = None
