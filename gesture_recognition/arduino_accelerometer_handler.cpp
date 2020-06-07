/* Copyright 2019 The TensorFlow Authors. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
==============================================================================*/

#include "accelerometer_handler.h"

#include <Arduino.h>
#include <Arduino_LSM9DS1.h>

#include "constants.h"

// A buffer holding the last 250 sets of 3-channel values
int NUM_SAMPLES_PER_CHUNK = 250;
int SAVE_DATA_LEN = 3 * NUM_SAMPLES_PER_CHUNK;
float save_data[750] = {0.0};

// Most recent position in the save_data buffer
int begin_index = 0;
// True if there is not yet enough data to run inference
bool pending_initial_data = true;
// How often we should save a measurement during downsampling
int sample_every_n;
// The number of measurements since we last saved one
int sample_skip_counter = 1;
// TODO: REPLACE WITH YOUR BUTTON PIN
int recordButton = A0;
int num_b_press;

enum states {STATE_WAITING, STATE_COLLECTING_PRESS_DATA, STATE_READY_FOR_INFERENCE};
int state;

TfLiteStatus SetupAccelerometer(tflite::ErrorReporter* error_reporter) {
  // Wait until we know the serial port is ready
  while (!Serial) {
  }

  // Switch on the IMU
  if (!IMU.begin()) {
    error_reporter->Report("Failed to initialize IMU");
    return kTfLiteError;
  }

  // Determine how many measurements to keep in order to
  // meet kTargetHz
  float sample_rate = IMU.accelerationSampleRate();
  sample_every_n = static_cast<int>(roundf(sample_rate / kTargetHz));

  error_reporter->Report("Magic starts!");
  pinMode(recordButton, INPUT);
  num_b_press = 0;
  state = STATE_WAITING;

  return kTfLiteOk;
}

bool ReadAccelerometer(tflite::ErrorReporter* error_reporter, float* input,
                       int len, bool reset_buffer) {
  // Clear the buffer if required, e.g. after a successful prediction
  if (reset_buffer) {
    memset(save_data, 0, SAVE_DATA_LEN * sizeof(float));
    begin_index = 0;
    pending_initial_data = true;
  }
  // Keep track of whether we stored any new data
  bool new_data = false;
  // Loop through new samples and add to buffer
  while (IMU.accelerationAvailable()) {
    float x, y, z;
    // Read each sample, removing it from the device's FIFO buffer
    if (!IMU.readAcceleration(x, y, z)) {
      error_reporter->Report("Failed to read data");
      break;
    }
    // Throw away this sample unless it's the nth
//    if (sample_skip_counter != sample_every_n) {
//      sample_skip_counter += 1;
//      continue;
//    }
    
//    error_reporter->Report("STATE: %d", state);
    int buttonVal = analogRead(recordButton); // TODO: update this if you use digitalRead
    int b = buttonVal >= 512 ? 1 : 0;
    if (state == STATE_WAITING) {
      if (b == 1) {
        // start collecting collecting data once button is pressed
        state = STATE_COLLECTING_PRESS_DATA;
      } 
    } else if (state == STATE_COLLECTING_PRESS_DATA) {
      if (b == 0) {
        // ready for inference once button is released
        state = STATE_READY_FOR_INFERENCE;
      } 
    }
    
    // Write samples to our buffer, converting to milli-Gs
    // and flipping y and x order for compatibility with
    // model (sensor orientation is different on Arduino
    // Nano BLE Sense compared with SparkFun Edge)
    save_data[begin_index++] = y * 1000;
    save_data[begin_index++] = x * 1000;
    save_data[begin_index++] = z * 1000;
    
    // Since we took a sample, reset the skip counter
//    sample_skip_counter = 1;
    // If we reached the end of the circle buffer, reset
    if (begin_index >= SAVE_DATA_LEN) {
      begin_index = 0;
    }
    new_data = true;
  }

  // Skip this round if data is not ready yet
//  if (!new_data) {
//    return false;
//  }

  // Check if we are ready for prediction or still pending more initial data
//  if (pending_initial_data && begin_index >= NUM_SAMPLES_PER_CHUNK) {
//    pending_initial_data = false;
//  }
//
//  // Return if we don't have enough data
//  if (pending_initial_data) {
//    return false;
//  }
  if (state == STATE_WAITING || state == STATE_COLLECTING_PRESS_DATA) return false;

  // Copy the requested number of bytes to the provided input tensor
  for (int i = 0; i < len; ++i) {
    int ring_array_index = begin_index + i - len; // begin ind: 0--> 750, len: 250
    if (ring_array_index < 0) {
      ring_array_index += SAVE_DATA_LEN;
    }
    input[i] = save_data[ring_array_index];
  }

  // IMPLIED: state == STATE_READY_FOR_INFERENCE
  state = STATE_WAITING; // start over
  return true;
  
//  if (state == STATE_READY_FOR_INFERENCE) {
//    state = STATE_WAITING; // start over
//    return true;
//  }
//  return false;
  
}
