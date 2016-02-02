"""
Created on 2 Feb 2016

Global Variables for the control logic
-   All variables set by main in the control logic are stored in the
    global variable class.  Global variables can be accessed from other
    classes, however, they are not set outside of main.py or simulator.py

"""




# list of all simulated components
simulated = set()
# functionQueue = []
# queueParameters = []
# boundaries = []
run = True
currentProcess = None
currentParams = None
taskStartTime = None
currentColumn = 0

bus = None
