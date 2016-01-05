Simulator
=========

This contains the simulator code, in Python, that simulates components of the ACMR Control System.

The simulator will use Zero MQ to communicate with the rest of the components.

### Running the Simulator Loop
- - -
#### Starting the Simulator

In order to run the simulator loop smoothly you should start the simulator first.

<pre><code>python main.py</code></pre>

The console should now show a line which represents the boat's current data. The order of variables are: `hog awa sog windSpeed latitude longitude rudderAngle sheetPercentage`

If you want extra debug information, use the parameter `-v` for a verbose debug display: it will output the True Wind Angle and Speed along with the header, current data, and old data.

Recommended: use the parameter `-r` for a fresh data file, this will also create the file if it does not yet exist.

To turn on gusts, which simulate bursts of strong winds every once and a while, use the parameter `-g`.

<pre><code>python main.py -v -r -g</code></pre>


### Structure of the Code
- - -
The code is akin to the code of TB 2013; there is a `standardcalc.py` file which contains most of the calculations, as well as a Vector2D class. Appropriate tests are contained in the appropriately named files, e.g. `tests_standardcalc.py`.

`sensors.py` contains the simulation code. Main calls the `update()` function every loop. The current time interval between each loop is 1 second. *If you change this, you must update the* `TIME_INTERVAL` *variable in* `sensors.py`.

### Simulator Logic

This section explains in detail the process of simulation, from the setup to the loop. This will help us pinpoint any simulation errors that we have, and it is always pretty cool to talk about virtual sailing physics anyways.

#### The Setup

In `sensors.py`, the simulator runs via a class called `Hardware`. All important constants are defined at the top of the class.

##### Constants

`WIND_ANGLE FLUCTUATIONS` the maximum amount of fluctuation (in degrees) in the simulated wind angle.

`WIND_SPEED_FLUCTUATIONS` the maximum amount of fluctuation (in meters/second) in the simulated wind speed.

`TIME_INTERVAL` the time between a call to `update()`. This might be changed to a console input variable.

`MAX_RUDDER_HOG_CHANGE` the change in the boat's heading caused by the rudder in a maximum position, as the boat travels over 1 meter.

`MAX_RUDDER_ANGLE` the maximum rudder setting possible. Currently set between -45 and 45.

`SOG_DECAY_FACTOR` this affects how fast the boat reaches the ideal SOG. The lower it is, the faster it will be.

##### Constructor (`__init__(self, verbose)`)

In the constructor, the simulator creates the template for the data with dictionaries: `self.currentData`, `self.oldData`, and the keys are the names of the data: `latitude`, `longitude`, `hog`, `cog`, `awa`, `sog`, `windSpeed`, `rudderAngle`, `sheetPercentage`.

The simulator proceeds to initialize several important simulation variables:

<pre><code>
self.trueWindAngle = random.randint(-180, 180)
self.trueWindSpeed = float(random.randint(5, 15))
self.displacement = standardcalc.Vector2D.zero()
self.windVelocity = standardcalc.Vector2D.zero()
self.boatVelocity = standardcalc.Vector2D.zero()
self.awaVelocity = standardcalc.Vector2D.zero()
</code></pre>

The true wind is set to a vector with a random speed from 5-15 m/s, and a direction anywhere from -180 to 180 degrees. _Note: this is the direction which the wind points to, not where it comes from._

All vectors are initialized to Zero Vectors, as they will be calculated in the loop.

The remaining code takes in the verbose argument for whether detailed debugging information is displayed, and the gust options are set to 0.

#### The Update Loop (`update(self)`)

The update loop is called every `TIME_INTERVAL` seconds, in this update loop, the simulator:

- Reads in data from the `mcuOutput` file.\
- Adjusts the boat according to simulated physics
- Outputs the data to `simulatorOutput` file.

##### adjustSOG

This adjusts the SOG based on these factors: the sheet settings, the apparent wind speed, and the apparent wind angle.

It first calculates a normalized number between 0 and 1 that represents the error of the actual `sheetSettings` to the ideal sheet settings in those conditions. When the sheet settings _are_ ideal, then this coefficient is 1. It drops off quickly once the error is larger than 10. Ideally, our MCU should always be calculating sheetSettings which are ideal, i.e. this value should always be 1.

Then, the maximum possible SOG is calculated, based on the apparent wind angle and the wind speed. Let's dive into this function `calculateMaxSOG(awa, windSpeed)`.

    # Returns maximum velocity at current apparent windspeed and awa
    def calculateMaxSOG(awa, windSpeed):
        awa = abs(awa)
        v1 = 12/(1+math.pow(math.e, -(windSpeed*0.6-5.5)))
    
        if awa < 40:
            v2 = 0
        elif awa < 45:
            v2 = 0.16*awa - 6.4
        elif awa < 115:
            v2 = -0.000163265306122*math.pow(awa, 2) + 0.0261224489796*awa - 0.    0448979591837
        elif awa < = 180:
            v2 = 0.000025641025641*math.pow(awa, 2) - 0.0137179487179*awa + 2.    03846153846
        else:
            raise Exception
    
        return v1 * v2

To do this, it first calculates an allowed boat speed based on the wind, `v1`. `v1` begins at 0 when `windSpeed` is 0, then climbs abruptly once `windSpeed` reaches around 10 or so.

Then, it calculates a second normalized (0 to 1) variable, `v2`, which depends on the awa. If the boat is in irons (awa < 45), `v2` is very small. Between 45 < awa < 115, `v2` follows a parabolic curve, where the max is approximately 75 degrees. 

`v1` is multiplied by `v2` to give the maximum SOG attainable. This maximum is then multiplied by the error coefficient we calculated.

Because the boat doesn't immediately jump to this calculated SOG, we adjust it gradually, adding only a fraction of the change in SOG. This is where the decay factor comes into play.

<pre><code>self.currentData['sog'] += (idealSOG - self.currentData['sog'])/self.SOG_DECAY_FACTOR</code></pre>

##### adjustHOG

This adjusts the HOG based on what the rudder angle is and what the speed of the boat is.

It calculates the `normalizedRudderRatio`, the ratio of the rudder angle to the max angle setting (`MAX_RUDDER_ANGLE`)

Then, it takes this fraction, and multiplies it by the maximum change in the HOG  through 1 meter. This will be the amount the boat turns through 1 meter, so another calculation is made to adjust for how far the boat travels. This calculation is simply the boat's SOG multiplied by `TIME_INTERVAL`.

Finally the angle is bound to 180.

##### adjustTrueWind

The true wind vector is allowed to fluctuate, via a bell curve function. Essentially, the fluctuations favor staying stable, but may deviate according to a bell curve.

##### adjustPosition

This function does all the dirty work of vector calculations. It first creates the vectors for true wind, apparent wind, and boat velocity. The apparent wind vector is calculated by subtracting the boat velocity from the true wind velocity.

The awa and the apparent windSpeed are extracted from the apparent wind vector.

*Note: since awa is defined as the angle of the apparent wind origin relative to the boat, we have to add the angle from the apparent wind vector to the angle from the boat's velocity.

After this, the displacement of the boat is calculated vector-style. This is then translated into coordinates via the function, `shiftCoordinates`.
