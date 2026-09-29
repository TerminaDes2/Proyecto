SYSTEM_THREAD(ENABLED); // for running with/without internet conection
#include "math.h" // libreria para funciones matematicas
#include "stdio.h" // libreria estándar de entradas salidas
int led = D7; // The on-board LED D7
void setup()
{
//Register a Particle function. We will call this function to turn the LED on and off
Particle.function("led",ledToggle);
// This is saying that when we ask the cloud for the function "led", it will employ the
function ledToggle() from this app.

// initialize the LED pin as an output.
pinMode(led, OUTPUT);
// set the LED to be OFF
digitalWrite(led, LOW);
}

// This routine loops forever
void loop()
{

}

// This function gets called whenever there is a matching API request
// the command string is simply '1' or a '0'

int ledToggle(String command) {
if (command=="1") {
digitalWrite(led,HIGH);
return 1;
}
else if (command=="0") {
digitalWrite(led,LOW);
return 0;
}
else {
return -1;
}
}