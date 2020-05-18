/*  This is essentially the same as our normal data logging function,
 *  however this updates slower, at a rate of timeToPrint milliseconds/second.  
 *  The slow down is there so in our script to draw live data, and there isn't a backlog
 *  of printed samples we haven't read yet (Arduino's loop runs at 117 kHz, can't run graph update
 *  this fast). timeToPrint should match the ms_delay in the graph update if we use the
 *  plot method in drawData.py
*/

#include <Arduino_LSM9DS1.h>

int recordButton = A0;
int timeToPrint = 100;
int startTime = 0;

void recordSerialData() {
  float x, y, z;

  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(x, y, z);
    int buttonVal = analogRead(recordButton);
    Serial.print(buttonVal >= 512 ? 1 : 0);
    Serial.print('\t');
    
    Serial.print(x);
    Serial.print('\t');
    Serial.print(y);
    Serial.print('\t');
    Serial.println(z);
  }
}

void setup() {
  Serial.begin(9600);
  while (!Serial);
  Serial.println("Started");

  pinMode(recordButton, INPUT);

  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  startTime = millis();
}

void loop() {
  if (millis() - startTime > timeToPrint) {
    recordSerialData();
    startTime = millis();
  }
}
