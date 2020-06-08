import numpy as np
import tensorflow as tf
import serial # import Serial Library


MODEL_PATH = "cnv.tflite" # TODO: update model path 
categories = {"C": 0, "A": 1, "T":2, ".":3} # TODO: update list of letters in correct order, matching train!


# MODEL_PATH = "model_lauren_AB.tflite" # TODO: update model path 
# categories = {"A": 0, "B": 1} # TODO: update list of letters in correct order, matching train!

# MODEL_PATH = "model_lauren_NOdone.tflite" # TODO: update model path 
# categories = {"N":0,"O":1,"done":2} # TODO: update list of letters in correct order, matching train!


SEQUENCE_LEN = 250 
STATE_WAITING_FOR_PRESS = 0
STATE_RECORDING = 1
STATE_WAITING_FOR_UNPRESS = 2
STATE_FINISHED = 3


######################  Get data samples!  ######################
def get_recording():
    print("Press Arduino button to begin recording")
    arduinoData = serial.Serial('COM3', 9600) #Creating our serial object named arduinoData
    recording = np.empty((1,3), dtype=np.float32) ## fixed length based on samples
    num_samples_rec = 0
    state = STATE_WAITING_FOR_PRESS

    # Records by getting the first SEQUENCE_LEN samples after pressing record button
    while state != STATE_FINISHED:
        # Wait here until there is data
        while (arduinoData.inWaiting()==0): 
            pass #do nothing
        # try: # trying to avoid occasional parsing errors with try/except
            # Read new data
        arduinoString = arduinoData.readline() #read the line of text from the serial port
        new_sample = np.array(arduinoString.decode().replace('\r\n','').split('\t')).astype(np.float32)-np.array([0,0,0,.98]).astype(np.float32)
        # Do nothing while waiting for button to start
        if state == STATE_WAITING_FOR_PRESS and new_sample[0] == 0: 
            continue
        # Transition to recording state & take first sample
        elif state == STATE_WAITING_FOR_PRESS and new_sample[0] == 1: 
            recording = np.array(new_sample[1:], dtype=np.float32).reshape(1,-1)
            num_samples_rec += 1
            state = STATE_RECORDING
        # Continue recording until sample is full
        elif state == STATE_RECORDING:
            recording = np.append(recording, new_sample[1:].reshape(1,-1), axis=0)
            num_samples_rec += 1
            if num_samples_rec == SEQUENCE_LEN: state = STATE_WAITING_FOR_UNPRESS
        elif state == STATE_WAITING_FOR_UNPRESS:
            state = STATE_FINISHED if (new_sample[0] ==0) else STATE_WAITING_FOR_UNPRESS
        # except: 
        #     continue


    ##### Run this after finishing data collection!
    arduinoData.close()

    return recording  # np.array((250,3))


######################  Run TFLite Model  ######################
def inference():
    # Load the TFLite model and allocate tensors.
    interpreter = tf.lite.Interpreter(model_path=MODEL_PATH)
    interpreter.allocate_tensors()

    # Get input and output tensors.
    input_details = interpreter.get_input_details()
    output_details = interpreter.get_output_details()

    # Test the model on random input data.
    input_shape = input_details[0]['shape']
    input_data = get_recording()
    input_data = input_data.reshape((1, SEQUENCE_LEN, 3, 1))
    print("Recording finished!")

    interpreter.set_tensor(input_details[0]['index'], input_data)

    interpreter.invoke()

    # The function `get_tensor()` returns a copy of the tensor data.
    # Use `tensor()` in order to get a pointer to the tensor.
    output_data = interpreter.get_tensor(output_details[0]['index']).squeeze()

    return post_process_probs(output_data)


######################  Process probabilities  ######################
def post_process_probs(probs):
    output_probs = {}
    for letter, indexer in categories.items():
        output_probs[letter] = probs[indexer]
    return output_probs

    

if __name__ == "__main__":
    # test 
    result = inference()
    print(result)





