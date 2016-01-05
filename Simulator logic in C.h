//Generator for the Sailbot hardware outputs
//Note: -integers and strings and c++ objects
//		-we can seed initial values

//add getters
class Simulator 
{
	public:
		void update(float rudderAngle, int sheetSetting);
	private: //add params
		Simulator();
		void adjustAwa();
		void adjustHog();
		void adjustSog();
		void adjustWSpd();
		void adjustGps_coords();
		void gps_convert();
		void genBell(float max);
		
		float dat[3][6];
		float TWS;
		float TWA;
}

//for cpp file
//Data we want:
//|---------------------------------------------------|
//|dat|   0   |   1   |   2   |   3   |   4   |   5   |
//|---------------------------------------------------|
//| 0 |  hog  |  awa  |  sog  |  wSpd |  lat  |  long |
//|---------------------------------------------------|
//| 1 | oldHog| oldAwa| oldSog|oldWSpd| oldLat|oldLong|
//|---------------------------------------------------|
//| 2 |  dHog |  dAwa |  dSog | dWSpd |  dLat | dLong |
//|---------------------------------------------------|
//Order: lat/long, hog, awa, sog, wSpd 

Simulator (){
	float dat[3][6] = {0}; //data array
	float TWS = 0; // true wind speed
	float TWA = 0; //true wind angle
}

void update(float rudderAngle, int sheetSetting) {// needs rudder angle and sheet settings
	for(int i=0; i<6; i++){
		dat[1][i] = dat[0][i]; // update old values to get current values
	}
	
	//change current values
	adjustGps_coords(dat[0][4], dat[0][5], dat[0][0], dat[0][2]); //this comes first because it will use the old values and doesn't affect the other calculations
	adjustHog(dat[0][1], rudderAngle, dat[0][2]); 2
	//dat[2][0] = dat[0][0]-dat[1][0]; //this delta is needed for the awa calculation
	adjustAwa(dat[0][0], dat[0][0]);
	adjustSog(dat[0][2], dat[0][1], sheetSetting, dat[0][3]);
	adjustWSpd(dat[0][3], TWS, dat[0][3], dat[0][1]);
	
	for(i=1; i<6; i++){
		dat[2][i] = dat[0][i]-dat[1][i]; // delta values get new values minus old values (except hog, whose delta has already been done)
	}
}

//awa: angle,(float)integer between -180 to 180
//behaviour: changes based on boat orientation and true wind angle
//relations: depends on hog and generated true wind angle and (ignored)sog
//input: current (old) apparent wing angle, true wind angle?

void adjustAwa(float* awa, float hog){//change to true wind
    TWA += genBell(180) //random change: maximum 180 degree wind switch
	awa = hog-TWA; //new value is difference between heading and true wind angle
}

//gps_coord: long floats (6 decimal?) with lat and long D+M/60+S/3600
//behaviour: alter by hog and sog converted into Cartesian movement
//relations depends on hog and sog
//inputs: current (old) coordinates, old heading, old speed, time change

void adjustGps_coords(float* lat, float* long, float hog, float sog){ //NEED TO * BY DELTA t
	lat += sog*cos(hog)/30.715/3600; //two last divisions convert to seconds, then to decimal degrees
	long += sog*sin(hog)/19.22/3600; //longitude distance taken at Greenwich latitude
}

void gps_convert(){//to change from string of latlong to separate values. Not yet needed
		
}

//hog: float? between -180 to 180
//behaviour: will trace out arc of sog length and angle relative to rudder setting
//relations: boat turns, so rudder angle and old sog
//inputs: current (old) heading, rudder setting, old speed, time change

void adjustHog(float* hog, float rudderAngle, float sog){ // NEED TO * BY DELTA t, rudder angle needs to be negative when turning to port
	float maxTurn = 10; //maximum turning rate with full rudder in degrees per metre. Needs calibration
	float nRudder = rudderAngle/rudderMax; //normalize the rudder angle
	float dThetaDD = nRudder*maxTurn; //the change in angle per meter is the normalized rudder angle times a maximum turn rate
	hog += dThetaDD*sog*DELTAt; // heading changes by the change in angle times the arc length times the time change
}

//sog: float? between 0 and inf
//behaviour: depends on sheets and awa/spd : Will need polar table
//relations: sheets and wind speeds, awa
//inputs: current (old) speed, wind angle, sheet percentage, old wind speeds

void adjustSog(float* sog, float awa, int sheets, float windspd){
	//ADD POLAR TABLE HERE
}

//cog: float? between -180 and 180
//behaviour: actual travel direction, hog affected by currents. Can be ignored for now
//relations: N/A

//windSpeed: float? between 0 and inf
//behaviour: change on random bell curve + change of that speed vector of the boat
//relations: depends on awa and old sog. True wind is just given as difference
//inputs: current (old) wind speed, current (old) true wind speed, speed, apparent wind angle

void adjustWSpd(float* spd, float* TWS, float sog, float awa){//use function for TWS (log function base 5?)
	TWS += gecnBell(20); //generates random change in true wind speed
	if(TWS < 0)
		TWS = 0; // True wind can't go negative
	spd = sqrt(TWS*TWS+sog*sog-2*TWS*sog*cos(awa)); //using the cosine law
}

//-------
//approximate bell curve function to generate random values for wind changes

int genBell(float max) {
	max = max/3 //divided by number of srands then *2 to be able to reach both positive and negative ends of max value
	float out = (srand(time(NULL))%max)+(srand(time(NULL))%max)+(srand(time(NULL))%max)+(srand(time(NULL))%max)
		+(srand(time(NULL))%max)+(srand(time(NULL))%max)-max*3; //approx. random Bell curve around 0 using six "dice". Last -max*x translates curve about 0
	
	return out;
}