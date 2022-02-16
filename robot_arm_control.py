import RPi.GPIO as GPIO
import time

#from rubik_cv_function import single_face_scanner

# Constants
SMALLSPEED = 1000 # movement speed for every small motor
BASESPEED = 200 # movement speed for every base motor
SMALL_MOTOR_DISTANCE = 1400
DIG_STATES = [GPIO.LOW, GPIO.HIGH]
ANGLE_MAPPING = {1: [50, 1],
                 2: [100, 1],
                 -1:[50, 0],
                 -2:[100,0]}

# Functions
# Motor basic functions
def single_step(step_pin, speed):
    '''
    This function turns the motor a single step.
    There is not much to it as it is called by other 
    functions.
    '''
    GPIO.output(step_pin, GPIO.HIGH)
    time.sleep(0.5/speed)
    GPIO.output(step_pin, GPIO.LOW)
    time.sleep(0.5/speed)
    
    return None
           
def revolutions(num_of_steps, claw_pins, speed, direction):
    '''
    This functions takes in a set number of steps and
    rotates the motor that many times. Using the motor
    resolution (steps per cycle) we can get the motor to 
    different positions. This function is also called by 
    other functions.
    '''
    for i in range(len(claw_pins[0])):
        GPIO.output(claw_pins[0][i], DIG_STATES[direction[i]])
       
    for i in range(num_of_steps):
        single_step(claw_pins[1], speed)

    return None
# Basic Moves
def back_off(face, angle, pin_dict):
    '''
    This serves to return the motor hands to the 
    proper position after a 90 degree turn. This will
    be explained more in a meeting. This is called by 
    both basic movement functions.
    '''
    turn_data = ANGLE_MAPPING[-angle]
    motor1 = pin_dict[face][1]
    motor2 = pin_dict[face][2]

    revolutions(SMALL_MOTOR_DISTANCE, motor2, SMALLSPEED, [0, 0])
    time.sleep(1)
    revolutions(turn_data[0], motor1, BASESPEED, [turn_data[1], turn_data[1]])
    time.sleep(1)
    revolutions(SMALL_MOTOR_DISTANCE, motor2, SMALLSPEED, [1, 1])

    return None
# Single face rotation    
def single_face_rotation(face, angle, pin_dict):
    '''
    This serves to perform a single face move. Moves
    for up face and down face are not included

    face -> front, back, right, left

    angle -> 1 (90 degree clockwise), 2 (180 degree clockwise)
             -1 (90 degree anti-clockwise)
    '''
    turn_data = ANGLE_MAPPING[angle]
    motor1 = pin_dict[face][1]
    if (angle == -1):
        back_off(face, angle, pin_dict)
    
    revolutions(turn_data[0], motor1, BASESPEED, [turn_data[1]])
    
    if (angle != -1):
        back_off(face, angle, pin_dict)

        
    return None

# Full cube rotation
def full_cube_rotation(axis, angle, pin_dict, back_off_flag):
    '''
    This serves to perform a full cube rotation. 
    This is mainly for picture taking but is used 
    for up and down rotations.

    axis - > x (front and back), y (right and left)

    angle -> 1 (90 degree clockwise), 2 (180 degree clockwise)
             -1 (90 degree anti-clockwise)
    '''
    turn_data = ANGLE_MAPPING[angle]

    if axis == 'y':
        x = [[pin_dict['right'][2][0][0], pin_dict['left'][2][0][0]], [pin_dict['right'][2][1][0], pin_dict['left'][2][1][0]]]
        y = [[pin_dict['front'][1][0][0], pin_dict['back'][1][0][0]], [pin_dict['front'][1][1][0], pin_dict['back'][1][1][0]]]

        if angle == -1:
            back_off("front", angle, pin_dict)
            back_off("back", angle, pin_dict)
        
        revolutions(SMALL_MOTOR_DISTANCE, x, SMALLSPEED, [0, 0])
        time.sleep(1)
        revolutions(turn_data[0], y, BASESPEED, [(turn_data[1] + 3) % 3, (turn_data[1] + 3) % 2])
        time.sleep(1)
        revolutions(SMALL_MOTOR_DISTANCE, x, SMALLSPEED, [1, 1])
        
        if back_off_flag == 1 and angle != -1:
            back_off("front", angle, pin_dict)
            back_off("back", angle, pin_dict)
        
    elif axis == 'x':
        x = [[pin_dict['right'][1][0][0], pin_dict['left'][1][0][0]], [pin_dict['right'][1][1][0], pin_dict['left'][1][1][0]]]
        y = [[pin_dict['front'][2][0][0], pin_dict['back'][2][0][0]], [pin_dict['front'][2][1][0], pin_dict['back'][2][1][0]]]

        if angle == -1:
            back_off("right", angle, pin_dict)
            back_off("left", angle, pin_dict)
            
        revolutions(SMALL_MOTOR_DISTANCE, y, SMALLSPEED, [0, 0])
        time.sleep(1)
        revolutions(turn_data[0], x, BASESPEED, [(turn_data[1] + 3) % 3, (turn_data[1] + 3) % 2])
        time.sleep(1)
        revolutions(SMALL_MOTOR_DISTANCE, y, SMALLSPEED, [1, 1])
        
        if back_off_flag == 1 and angle != -1:
            back_off("right", angle, pin_dict)
            back_off("left", angle, pin_dict)
    return None

# Special Moves
def special_face_rotations(face, angle, pin_dict):
    '''
    This serves to perform a single face move for 
    the up face and the down face.

    face -> up, down

    angle -> 1 (90 degree clockwise), 2 (180 degree clockwise)
             -1 (90 degree anti-clockwise)
    '''
    if face == "up":
        full_cube_rotation("y", 1, pin_dict, 1)
        single_face_rotation("front", angle, pin_dict)
        full_cube_rotation("y", -1, pin_dict, 1)
    elif face == "down":
        full_cube_rotation("y", -1, pin_dict, 1)
        single_face_rotation("front", angle, pin_dict)
        full_cube_rotation("y", 1, pin_dict, 1)
    return None

