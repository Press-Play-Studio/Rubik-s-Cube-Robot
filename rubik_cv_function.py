from skimage import color, morphology
from skimage.transform import hough_line, hough_line_peaks, rotate
from skimage.feature import canny
from skimage.filters import threshold_otsu
from cv2 import VideoCapture
import cv2
import time
import numpy as np
def single_face_scanner(input_image):

    '''
    The aim of this function is to take a single image of one
    face of the rubik's cube and retreive the colors each 
    cublets color in form of a matrix
    '''
#Isolating possible color range

    # convert image to hsv
    imageHSV = cv2.cvtColor(input_image, cv2.COLOR_RGB2HSV)

    # compute hsv range
    min_HSV = np.array([0, 0, 128], dtype = "uint8")
    max_HSV = np.array([255, 255, 255], dtype = "uint8")

    # generate binary image of color within range
    rubik_range_HSV = cv2.inRange(imageHSV, min_HSV, max_HSV)

    # use morphology to remove artifacts and fill holes
    rubik_range_HSV = morphology.area_opening(rubik_range_HSV, area_threshold = 1000)
    rubik_range_HSV = morphology.area_closing(rubik_range_HSV, area_threshold = 1000)

    #Isolating edges in image
    edge = canny(rubik_range_HSV, sigma = 0.1)
    edge = morphology.binary_dilation(edge)



# Isolate cube location from egde image

    # get angle of most prominent line
    angles = np.linspace(0, np.pi * 2, 360, endpoint=False)
    h, theta, d = hough_line(edge, theta=angles)

    _, prominent_angle, _= hough_line_peaks(h, theta, d, num_peaks=2)

    try:
        prominent_angle = prominent_angle[0] * (180/np.pi)

        # get level of skew from the origin
        if prominent_angle > -10 and prominent_angle < 10:
            prominent_angle -= 0 
        elif prominent_angle > 80 and prominent_angle < 100:
            prominent_angle -= 90
        elif prominent_angle > 170 and prominent_angle < 190:
            prominent_angle -= 180
        elif prominent_angle > 260 and prominent_angle < 280:
            prominent_angle -= 270
        elif prominent_angle > 350 and prominent_angle < 370:
            prominent_angle -= 360

        # rotate image to adjust deviation from origin
        edge = rotate(edge, prominent_angle, preserve_range=True).astype("int")
        imageHSV = rotate(imageHSV, prominent_angle, preserve_range=True).astype("int")
    except:
        pass

    xbased = []
    ybased = []

    # isolate lines immediately surrounding cube
    angles = np.linspace(0, np.pi * 2, 360, endpoint=False)
    h, theta, d = hough_line(edge, theta=angles)

    for _, angle, dist in zip(*hough_line_peaks(h, theta, d, threshold = 0.4 * np.max(h))):
    
        # point in a line
        (x0, y0) = dist * np.array([np.cos(angle), np.sin(angle)])
        
        # angle of the line from the origin
        angle = round(angle * (2 / np.pi))
        
        
        for i in range(2):
            if 3 > angle:
                angle += 2
        if angle == 3:
            if (y0 > 0) and (y0 < edge.shape[0]):
                ybased.append(y0)
        
        if angle == 4:
            if (x0 > 0) and (x0 < edge.shape[1]):
                xbased.append(x0)

    # coordinates of best crop
    x1 = int(max(xbased))
    x2 = int(min(xbased))
    y1 = int(max(ybased))
    y2 = int(min(ybased))

    # cropped_image_obtained
    cropped = imageHSV[y2:y1,x2:x1,:]
    croppedrgb = input_image[y2:y1,x2:x1,:]
    #cv2.imshow('1',croppedrgb)
    #cv2.waitKey(0)
    
# Determine color map of isolated face
    color_matrix = np.zeros((3,3))
    height = cropped.shape[0]
    width = cropped.shape[1]

    for row in range(3):
        for col in range(3):

            median = np.median(croppedrgb[row * (height // 3) : (row + 1) * (height // 3), 
                                  col * (width // 3) : (col + 1) * (width // 3), :], axis = (0,1))

            
            median = color.rgb2hsv(median[::-1])
            median[0] *= 360
            median[1] *= 100
            median[2] *= 100/255

            if (median[1] < 22):
                    color_matrix[row][col] = 1
            else:
                if (median[0] < 1):
                    color_matrix[row][col] = 6
                elif (median[0] >= 1) and (median[0] < 41):
                    color_matrix[row][col] = 2
                elif (median[0] >= 41) and (median[0] < 92):
                    color_matrix[row][col] = 3
                elif (median[0] >= 92) and (median[0] < 171):
                    color_matrix[row][col] = 4
                elif (median[0] >= 180) and (median[0] < 260):
                    color_matrix[row][col] = 5
                elif (median[0] >= 340) and (median[0] < 360):
                    color_matrix[row][col] = 6

    return color_matrix

'''
colors = {0:"none",1:"w", 2:"o", 3:"y", 4:"g", 5:"b", 6:"r"} 
cube = ""
cam = VideoCapture(0)
print("done")
########################################################
#
# This  should be the scan loop
#
########################################################
np.set_printoptions(threshold=np.inf)
for i in range(6):

    # We should get feedback on if the device is ready to scan 
    # before the scanning process starts. This feedback should 
    # probably go here.

    for i in range(5):
        index, input_image = cam.read(1)
    cv2.imshow('1', input_image)
    cv2.waitKey(0)
        
    # run face scanner on image
    face_mapping = single_face_scanner(input_image)
    print(face_mapping)
    # convert color matrix to string input.
    for row in range(3):
       for col in range(3):
            cube += colors[face_mapping[row][col]]

########################################################

#solution = utils.solve(cube, 'Kociemba')
'''