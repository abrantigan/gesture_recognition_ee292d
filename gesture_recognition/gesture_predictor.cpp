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

#include "gesture_predictor.h"

#include "constants.h"


// The result of the last prediction
int last_predict = -1;

// Return the result of the last psediction
int PredictGesture(float* output) {
  int this_predict = -1;
  float max_predict_prob = 0.0f;
  for (int i = 0; i < NUM_GESTURES; i++) {
    if (output[i] > max_predict_prob) {
      this_predict = i;
      max_predict_prob = output[i];
    } 
  }
  return this_predict;
}
