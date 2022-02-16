import RPi.GPIO as GPIO
from cv2 import VideoCapture
from rubik_solver import utils
from robot_arm_control import back_off, single_face_rotation, full_cube_rotation,special_face_rotations
from rubik_cv_function import single_face_scanner

# setup
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

# pins for front arm
front10 = 3 # front arm base motor dir pin
front11 = 5 # front arm base motor step pin

front20 = 23 # front arm small motor dir pin
front21 = 29 # front arm small motor step pin

# pins for back arm
back10 = 8 # back arm base motor dir pin
back11 = 10 # back arm base motor step pin

back20 = 31 # back arm small motor dir pin
back21 = 33 # back arm small motor step pin

# pins for right arm
right10 = 13 # right arm base motor dir pin
right11 = 15 # right arm base motor step pin

right20 = 35 # right arm small motor dir pin
right21 = 37 # right arm small motor step pin

# pins for left arm
left10 = 19 # left arm base motor dir pin
left11 = 21 # left arm base motor step pin

left20 = 38 # left arm small motor dir pin
left21 = 40 # left arm small motor step pin

# DON'T TOUCH PLEAAAAASSSEEEEE--------------------------------------------------------
GPIO.setup(front10, GPIO.OUT)
GPIO.setup(front11, GPIO.OUT)
GPIO.setup(front20, GPIO.OUT)
GPIO.setup(front21, GPIO.OUT)
GPIO.setup(back10, GPIO.OUT)
GPIO.setup(back11, GPIO.OUT)
GPIO.setup(back20, GPIO.OUT)
GPIO.setup(back21, GPIO.OUT)
GPIO.setup(right10, GPIO.OUT)
GPIO.setup(right11, GPIO.OUT)
GPIO.setup(right20, GPIO.OUT)
GPIO.setup(right21, GPIO.OUT)
GPIO.setup(left10, GPIO.OUT)
GPIO.setup(left11, GPIO.OUT)
GPIO.setup(left20, GPIO.OUT)
GPIO.setup(left21, GPIO.OUT)

'''
pin dictionary:
    - Index level 1 (direction or arm) -> front,
                                          back,
                                          left,
                                          right
                                          
        - Index level 2 (motor size) -> 1 = base or big,
                                        2 = small
                                        
            - Index level 3 (motor pin) -> 0 = direction pin,
                                           1 = step pin
'''
pin_dict = {"front":{1: [[front10], [front11]], 2: [[front20], [front21]]},
            "back":{1: [[back10], [back11]], 2: [[back20], [back21]]},
            "right":{1: [[right10], [right11]], 2: [[right20], [right21]]},
            "left":{1: [[left10], [left11]], 2: [[left20], [left21]]},}

#Main Loop
scanning_loop = [['x', 1, 1], ['y', 1, 1], ['x', -1, 1], ['x', -1, 1],
                 ['x', -1, 1], ['y', 1, 1], ['x', 1, 0], ['y', 1, 0], ['x', 1, 0]]

colors = {0:"none",1:"w", 2:"o", 3:"y", 4:"g", 5:"b", 6:"r"} 
cube = ""
cam = VideoCapture(0)
for i in range(5):
    index, input_image = cam.read(1)
# scanning loop
for scan in scanning_loop:
    # rotate to proper position
    full_cube_rotation(scan[0], scan[1], pin_dict, 0)
    
    #take picture
    if scan[2] == 1:
        for i in range(5):
            index, input_image = cam.read(1)
            
        # run face scanner on image
        face_mapping = single_face_scanner(input_image)
        print(face_mapping)
        
        # convert color matrix to string input.
        for row in range(3):
           for col in range(3):
                cube += colors[face_mapping[row][col]]
    
    # perform back-off
    if scan[0] == 'y':
        back_off("front", scan[1], pin_dict)
        back_off("back", scan[1], pin_dict)
    else:
        back_off("left", scan[1], pin_dict)
        back_off("right", scan[1], pin_dict)
        
cube = 'wowgybwyogygybyoggrowbrgywrborwggybrbwororbwborgowryby'
solution = utils.solve(cube, 'Kociemba')

for move in solution:
    current_move = str(move)
    if len(current_move) == 1:
        current_move += "1"
    if current_move[1] == "'":
        current_move[1].replace("'","0")  

    move_dict = {"F": "front",
                 "B": "back",
                 "R": "left",
                 "L": "right",
                 "U": "up",
                 "D": "down"}
    
    if current_move[0] in ["F","L","R","B"]:
        if current_move[1] in ["1", "2"]:
            single_face_rotation(move_dict[current_move[0]], int(current_move[1]), pin_dict)
        else:
            single_face_rotation(move_dict[current_move[0]], -1, pin_dict)

        
    if current_move[0] in ["U","D"]:
        if current_move[1] in ["1", "2"]:
            special_face_rotations(move_dict[current_move[0]], int(current_move[1]), pin_dict)
        else:
            special_face_rotations(move_dict[current_move[0]], -1, pin_dict)



