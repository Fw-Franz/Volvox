/* This example shows how to display a moving rainbow pattern on
 * an APA102-based LED strip. */

/* By default, the APA102 library uses pinMode and digitalWrite
 * to write to the LEDs, which works on all Arduino-compatible
 * boards but might be slow.  If you have a board supported by
 * the FastGPIO library and want faster LED updates, then install
 * the FastGPIO library and uncomment the next two lines: */
// #include <FastGPIO.h>
// #define APA102_USE_FAST_GPIO


#include <APA102.h>

// Define which pins to use.
const uint8_t dataPin1 = 6;
const uint8_t dataPin2 = 8;
const uint8_t dataPin3 = 10;

void setup()
{
  //Serial.begin(9600);
}

/* Converts a color from HSV to RGB.
 * h is hue, as a number between 0 and 360.
 * s is the saturation, as a number between 0 and 255.
 * v is the value, as a number between 0 and 255. */

int timepoint=0;

int timepoint_cycles=0;
int number_of_cycles=4; //eeach cycle is 3.75 min, so 4 cycles are 15min

int random_mat[]={1,1,0,0,1,0,1,0,1,0,0,0,1,1,0,0,0,1,1,1,0,1,0,1,1,1,1,0,1,1,0,1,1,0,0,1,1,1,0,1,1,0,0,0,0,1,0,1,1,1,0,0,0,1,1,1,0,1,1,1,0,1,0,0,1,0,0,1,0,0,0,0,0,0,1,0,0,0,1,0,0,0,1,1,0,0,1,0,0,1,1,0,0,0,1,0,1,1,1,0,1,1,1,1,1,0,0,0,1,0,0,1,1,0,1,1,0,1,1,1,0,0,1,0,1,1,1,1,1,0,1,1,0,0,1,1,1,1,0,0,1,1,0,1,1,0,1,0,1,1,1,0,0,0,1,1,0,1,0,1,1,0,1,1,0,0,1,0,1,1,0,1,1,0,0,0,1,0,0,0,1,0,0,1,0,1,1,1,0,1,1,0,0,0,1,1,1,0,1,1,1,1,1,1,0,0,1,1,1,0,1,1,0,0,1,0,0,1,1,1,0,1,0,0,1,1,0,0,0,1,1,1,0,0,1,0,1,1,1,1,0,0,0,1,0,0,0,0,1,1,0,0,1,1,1,0,1,0,0,0,1,0,0,1,0,1,1,1,1,1,0,0,1,0,0,1,1,0,1,1,1,0,0,1,0,0,0,1,1,1,0,1,0,1,0,1,0,1,1,1,1,1,0,1,1,0,0,1,0,0,0,1,1,1,0,0,1,0,0,1,1,1,1,0,0,1,0,1,1,1,1,1,0,0,1,0,1,1,1,0,0,1,1,0,0,1,1,0,1,0,0,0,0,1,1,1,1,0,0,0,0,1,1,0,1,0,1,0,0,0,1,1,1,1,0,0,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,1,1,1,0,0,0,1,0,1,0,1,0,1,1,0,1,0,1,1,0,1,0,1,0,0,1,1,1,0,1,0,1,1,1,1,1,0,1,1,1,1,0,1,0,1,0,1,0,0,1,1,0,0,1,0,1,0,1,1,0,1,1,1,1,1,0,0,1,0,1,0,1,0,1,0,0,1,1,0,0,0,1,0,1,1,0,0,1,0,0,1,0,0,0,1,0,1,0,0,0,1,0,0,1,1,0,0,0,1,0,0,0,0,1,1,0,0,0,1,1,0,0,1,0,1,1,0,0,1,1,0,1,1,1,0,0,0,1,0,0,1,1,1,0,0,0,1,0,1,0,1,0,0,0,1,0,0,0,0,1,1,1,0,0,1,0,0,0,0,0,1,0,0,1,1,1,1,1,0,0,1,0,1,1,0,1,1,1,0,0,0,0,1,1,1,0,0,1,1,0,0,0,1,0,0,0,1,0,0,0,1,0,0,1,1,1,1,0,0,1,1,1,1,0,0,0,1,1,0,1,0,0,0,1,0,1,1,1,1,0,0,0,1,1,0,0,0,0,0,0,1,1,0,1,0,1,0,0,0,0,0,1,1,1,1,0,1,0,1,0,1,0,0,1,1,1,1,1,1,1,0,0,0,1,1,0,0,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,1,0,1,1,0,0,1,0,1,0,0,1,1,1,1,1,1,0,0,0,1,0,1,1,1,0,0,0,1,0,0,1,1,1,1,1,0,1,1,1,1,0,1,1,1,1,0,0,1,0,0,1,0,1,1,0,1,1,0,1,1,0,1,0,0,1,1,0,0,0,0,1,1,1,1,1,0,1,1,0,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,0,1,0,0,0,1,1,0,0,1,0,0,1,0,0,0,0,0,1,0,0,1,0,0,1,1,1,1,1,1,0,0,1,0,1,1,0,0,1,1,0,1,1,0,0,1,0,0,0,0,0,0,1,1,1,1,1,0,1,0,1,1,1,1,1,1,0,1,1,0,1,1,1,0,1,1,1,0,0,0,0,1,1,0,0,0,0,0,1,0,0,1,0,0,0,1,0,0,0,1,1,0,0,1
};
int x_f=0;
int x_r=0;
int x_c=1;

  
void loop()
{
  //uint8_t time = millis() >> 4;
  uint8_t time = millis();

  if (timepoint>899){
    timepoint_cycles=timepoint_cycles+1;
    timepoint=0;
  }
  
  // fixed time series:
  if ((int(timepoint/2)+1) % 2 == 0 ){
    x_f=0;
  }  
  else {
    x_f=1;
  }
  // random time series:
  if (random_mat[timepoint] == 1 ){
    x_r=1;
  }
  else {
    x_r=0;
  }

  digitalWrite(dataPin1,x_r);
  digitalWrite(dataPin2,x_c);  
  digitalWrite(dataPin3,x_f);

  if (timepoint_cycles>number_of_cycles-1){
    digitalWrite(dataPin1,0);
    digitalWrite(dataPin2,0);
    digitalWrite(dataPin3,0);
    while(1){}
  }

  timepoint=timepoint+1;
  delay(249);
}
