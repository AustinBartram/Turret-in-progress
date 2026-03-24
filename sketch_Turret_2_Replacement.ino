#include <Servo.h> // library in use, Allows for the control of servos

//-----Declare servos and variables
Servo  recoil_servo;
Servo pan_servo;
Servo tilt_servo;

const byte pan_limit_left  = 0; //pan from L to R, full left movement(0) to right(180)
const byte pan_limit_right = 180;

const byte tilt_limit_down = 65; //starts at 65 so as to not hit the frame. Downward point
const byte tilt_limit_up= 180; // allows for the tilt of the turret on the y and Z axis. This is pointing up 

const byte recoil_rest = 180;    // Angle of the servo  when at rest
const byte recoil_pushed = 125;  // Angle the servo need to reach  to push the dart


//-----Variables related to serial data handling
byte  byte_from_app;
const byte buffSize = 30;
byte inputBuffer[buffSize];

const  byte startMarker = 255;
const byte endMarker = 254;

byte bytesRecvd = 0;
boolean  data_received = false;


//-----Variable related to motor timing and firing
bool  is_firing =  false;
bool can_fire =  false;

// removed bool recoiling as it is never used
// FIX: Since recoiling was removed, the check using it must also be removed

//unsigned  long firing_start_time = 0;
/**
*Since we dont store surrent_time We can change unsigned long firing_current_time = 0; to
* unsigned long now = millis();
* unsigned long elapsed = now - fire_start_time;
*/

//unsigned long now = millis();
//unsigned long elapsed = now - fire_start_time;

/**
*had const long firing_time = 150;
 but for improvement millis() returns unsigned long. And the best practice would be to have 
* const unsigned long firing_time = 150; This prevents signed/unsigned comparison warnings, rollover issues, and matches type/Millis.
*/

const unsigned long firing_time = 150;

/* -------- FIX ADDED VARIABLES -------- */
unsigned long firing_start_time = 0;
unsigned long firing_current_time = 0;
/* ------------------------------------- */

unsigned long recoil_start_time = 0;
unsigned long  recoil_current_time = 0;

const long recoil_time = 2 * firing_time;

const  byte motor_pin =  12;

boolean motors_ON = false;


//===========================
void  setup()
{
  //-----define motor pin mode
  pinMode(motor_pin, OUTPUT);
  digitalWrite(motor_pin, LOW);

  //-----attaches servo to pins
  recoil_servo.attach(9);
  pan_servo.attach(10);
  tilt_servo.attach(11);

  //-----starting sequence
  recoil_servo.write(recoil_rest);
  pan_servo.write(90);

  delay(1000);

  tilt_servo.write(105);

  Serial.begin(9600);  // begin serial communication
}


//===========================
void  loop()
{
  getDataFromPC();

  //removed repetitive set_motor(), No need to call twice
  if (data_received) {

    move_servo();
    set_recoil();
    set_motor();

    data_received = false; //makes packet processing smoother and more atomic
  }

  fire();
}


//===========================
void  getDataFromPC() {

//expected structure of data [start byte, pan amount,  tilt amount, motor on, firing button pressed, end byte]
//start byte = 255
//pan amount = byte between 0 and 253
//tilt amount = byte between 0 and  253
//motor on = 0 for off - 1 on
//firing button pressed = 0 for not  pressed - 1 for pressed
//end byte = 254


/**
	• Changed from an if statement to a while loop. 
  */

  while (Serial.available() > 0) {  // If data available in serial / reads all the available bytes

    byte_from_app = Serial.read();   //read  the next character available

    /**
    *starting the marker
    */

    if (byte_from_app == startMarker) {     // look  for start byte, if found:

      bytesRecvd = 0;                   //reset byte  received to 0(to start populating inputBuffer from start)
      data_received  = false; //new packet starting
    }

    /**
    * Ending Marker
    */

    else if (byte_from_app == endMarker) {    // look for end  byte, if found:

      /**
      *Only accepts the packet if there are a correct number of bytes recieved
      */

      if (bytesRecvd >= 4) {
        data_received = true;                // set data_received  to true so the data can be used
      }

      /**
      *This is purely optional but also prevents an accidental overflow reuse
      */

      bytesRecvd = 0;
    }

    /**
    * Normal type of data, Checks before writing the bounds. *C*
    */

    else {

      if (bytesRecvd < buffSize) {

        inputBuffer[bytesRecvd] = byte_from_app;
        bytesRecvd++;

      }
      else {

        bytesRecvd = buffSize - 1;

      }

    }

  }

}


//===========================
void  move_servo() {

  byte pan_servo_position = map(inputBuffer[0], 0, 253,  pan_limit_left, pan_limit_right);//convert inputbuffer value to servo position value
  pan_servo.write(pan_servo_position); //set pan servo position

  byte tilt_servo_position  = map(inputBuffer[1], 0 , 253, tilt_limit_up, tilt_limit_down); //convert inputbuffer  value to servo position value
  tilt_servo.write(tilt_servo_position); //set  pan servo position

}


//===========================
void set_recoil()  {

  if (inputBuffer[3] == 1) {        //if fire button pressed

    // FIX: removed !recoiling because variable no longer exists
    if  (!is_firing) { //and not already firing
      can_fire  = true;              //set can fire to true (see effect in void fire())
    }

  }

  else {                  // if fire button not pressed

    can_fire =  false;     //set can fire to false (see effect in void fire())

  }

}


//===========================
void  set_motor() {

//-----start and stop motors using MOSFET transisitor .

  if (inputBuffer[2] == 1) {                //if screen touched

    digitalWrite(motor_pin,  HIGH);          //turn motor ON
    motors_ON = true;

  }

  else {                                   //if  screen not touched

    digitalWrite(motor_pin, LOW);          //turn motor OFF
    motors_ON = false;

  }

}


//===========================
void  fire() { //if motor byte on, turn motor on and check for time it has been on

  if (can_fire && !is_firing && motors_ON) {

    //if (can_fire && !is_firing)  {

    firing_start_time = millis();
    recoil_start_time = millis();

    is_firing = true;
  }

  firing_current_time = millis();
  recoil_current_time  = millis();

  if (is_firing && firing_current_time - firing_start_time <  firing_time) {

    recoil_servo.write(recoil_pushed);

  }

  else if (is_firing  && recoil_current_time - recoil_start_time < recoil_time) {

    recoil_servo.write(recoil_rest);

  }

  else if (is_firing && recoil_current_time - recoil_start_time > recoil_time)  {

    is_firing = false;

  }

}