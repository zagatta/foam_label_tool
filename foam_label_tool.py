import json
from json import JSONDecodeError
import cv2 as cv
import numpy as np
import argparse
from simple_term_menu import TerminalMenu
import os
from os import walk
import copy
from scipy import stats
import math
import json

# https://stackoverflow.com/questions/8664866/draw-perpendicular-line-to-a-line-in-opencv
def getPerpCoord(aX, aY, bX, bY, length):
    '''
    c and d will be placed perpendicular to b
    '''
    vX = bX-aX
    vY = bY-aY
    #print(str(vX)+" "+str(vY))
    if(vX == 0 or vY == 0):
        return 0, 0, 0, 0
    mag = math.sqrt(vX*vX + vY*vY)
    vX = vX / mag
    vY = vY / mag
    temp = vX
    vX = 0-vY
    vY = temp
    cX = bX + vX * length
    cY = bY + vY * length
    dX = bX - vX * length
    dY = bY - vY * length
    return int(cX), int(cY), int(dX), int(dY)

class Constants:
    """Constants for this module."""
    SEPARATOR = "_"
    GAMMA = "gamma"
    ENUMARATION_OFFSET = 1
    PPI_STRING = "PPI"
    RETICULATED_SIGNIFIER = "Reti"
    SIDES = ["1", "2", "3", "4", "all"]
    IMG_HEIGHT = 720
    IMG_WIDTH = 1280
    LINE_THICKNESS_BIG = 2
    LINE_THICKNESS_THIN = 1
    GREEN = (0, 255, 0)
    BLUE = (255, 165, 0)
    ORANGE = (0, 89, 255)
    JSON = ".json"

class DrawOps:
    
    # draw a line https://stackoverflow.com/questions/18632276/how-to-draw-a-line-on-an-image-in-opencv
    @staticmethod
    def draw_line(event,x,y,flags,param):
            global mouseX,mouseY
            if event == cv.EVENT_LBUTTONDBLCLK:
                print("click")
                mouseX,mouseY = x,y
                cv.line(param[0], (x, y), (x+200, y+200), (0, 255, 0), thickness=Constants.LINE_THICKNESS_BIG)
                cv.imshow(title ,img)

    @staticmethod
    def draw_knot(event,x,y,flags,param):
            if event == cv.EVENT_LBUTTONDBLCLK:
                title = param[0]
                img = param[1]
                knots = param[2]
                center = param[3]
                if len(knots[0].coordinates) < 3:
                    print("adding new point for knot1 - " + str(x) + ":" + str(y))
                    knot = knots[0]
                else:
                    print("adding new point for knot2 - " + str(x) + ":" + str(y))
                    knot = knots[1]
                knot.addPoint(x, y)
                if not len(knot.coordinates) < 3:
                    cv.line(img, (knot.coordinates[0][0], knot.coordinates[0][1]), (knot.coordinates[1][0], knot.coordinates[1][1]), (0, 255, 0), thickness=Constants.LINE_THICKNESS_THIN)
                    cv.line(img, (knot.coordinates[1][0], knot.coordinates[1][1]), (knot.coordinates[2][0], knot.coordinates[2][1]), (0, 255, 0), thickness=Constants.LINE_THICKNESS_THIN)
                    cv.line(img, (knot.coordinates[2][0], knot.coordinates[2][1]), (knot.coordinates[0][0], knot.coordinates[0][1]), (0, 255, 0), thickness=Constants.LINE_THICKNESS_THIN)
                if not len(knots[0].coordinates) < 3 and not len(knots[1].coordinates) < 3:
                    print("both knots drawn")
                    center1 = ((knots[0].coordinates[0][0]+knots[0].coordinates[1][0]+knots[0].coordinates[2][0])//3, (knots[0].coordinates[0][1]+knots[0].coordinates[1][1]+knots[0].coordinates[2][1])//3) 
                    center.append(center1)
                    center2 = ((knots[1].coordinates[0][0]+knots[1].coordinates[1][0]+knots[1].coordinates[2][0])//3, (knots[1].coordinates[0][1]+knots[1].coordinates[1][1]+knots[1].coordinates[2][1])//3) 
                    center.append(center2)
                    cv.line(img, (center[0][0], center[0][1]), (center[1][0], center[1][1]), (0, 255, 0), thickness=Constants.LINE_THICKNESS_THIN)
                cv.imshow(title ,img)
    
    @staticmethod
    def measurement(event,x,y,flags,param):
        title = param[0]
        img = param[1]
        measurement = param[2]
        center = param[3]
        measurement_spots = param[4]
         # https://www.geeksforgeeks.org/copy-python-deep-copy-shallow-copy/
        draw_img = copy.deepcopy(img) 
        if len(measurement.distances) < 2:
            spot_index = 0
        elif len(measurement.distances) < 4:
            spot_index = 1
        else:
            spot_index = 2
        if len(measurement.distances) < 6:
            #currently using the spot with index+1 from how big our measured distances array is
            spot = (measurement_spots[spot_index][0], measurement_spots[spot_index][1])
            dist = math.hypot(spot[0] - x, spot[1] - y)
            perpCoord = getPerpCoord(center[0][0], center[0][1], measurement_spots[spot_index][0], measurement_spots[spot_index][1], dist)
            if(len(measurement.distances) % 2) == 0:
                #gerade
                (i1, i2) = (0, 1)
            else:
                #ungerade
                (i1, i2) = (2, 3)
            if event == cv.EVENT_MOUSEMOVE:
                cv.line(draw_img, (spot), (perpCoord[i1], perpCoord[i2]), (100, 100, 0), thickness=Constants.LINE_THICKNESS_THIN)
                cv.imshow(title , draw_img)
            if event == cv.EVENT_LBUTTONDBLCLK:
                measurement.add_measurement(spot, (perpCoord[i1], perpCoord[i2]))

    @staticmethod
    def show(img, title, measurement, knots, center):
        for knot in knots:
            cv.line(img, (knot.coordinates[0][0], knot.coordinates[0][1]), (knot.coordinates[1][0], knot.coordinates[1][1]), Constants.GREEN, thickness=Constants.LINE_THICKNESS_THIN)
            cv.line(img, (knot.coordinates[1][0], knot.coordinates[1][1]), (knot.coordinates[2][0], knot.coordinates[2][1]), Constants.GREEN, thickness=Constants.LINE_THICKNESS_THIN)
            cv.line(img, (knot.coordinates[2][0], knot.coordinates[2][1]), (knot.coordinates[0][0], knot.coordinates[0][1]), Constants.GREEN, thickness=Constants.LINE_THICKNESS_THIN)
        #knot-center-line
        cv.line(img, center[0], center[1], Constants.BLUE, thickness=Constants.LINE_THICKNESS_THIN)
        #measurements 
        i = 0
        for line in measurement.distances:
            cv.line(img, (line[0][0], line[0][1]), (line[1][0], line[1][1]), Constants.ORANGE, thickness=Constants.LINE_THICKNESS_THIN)
            # https://www.geeksforgeeks.org/python-opencv-cv2-puttext-method/
            org_x = line[1][0] 
            org_y = line[1][1]
            text = str(int(measurement.getPx(i)))
            org = (org_x, org_y)
            cv.putText(img, text, org, cv.FONT_HERSHEY_SIMPLEX,  1, Constants.ORANGE, 1, cv.LINE_AA, False) 
            i += 1
        text = str(int(measurement.getThickness()))
        org = (center[0])
        cv.putText(img, text, org, cv.FONT_HERSHEY_SIMPLEX,  1, Constants.BLUE, 1, cv.LINE_AA, False) 
        cv.imshow(title , img)
        
    
        

class Measurement:
    def __init__(self):
        self.distances = []

    def add_measurement(self, start, end):
        self.distances.append([start, end])

    def getThickness(self):
        #dist = math.hypot(x2-x1, y2-y1)
        '''
        dist10_1 = math.hypot(self.distances[0][0][0] - self.distances[0][1][0], self.distances[0][0][1] - self.distances[0][1][1])
        dist10_2 = math.hypot(self.distances[1][0][0] - self.distances[1][1][0], self.distances[1][0][1] - self.distances[1][1][1])
        dist90_1 = math.hypot(self.distances[2][0][0] - self.distances[2][1][0], self.distances[2][0][1] - self.distances[2][1][1])
        dist90_2 = math.hypot(self.distances[3][0][0] - self.distances[3][1][0], self.distances[3][0][1] - self.distances[3][1][1])
        dist50_1 = math.hypot(self.distances[4][0][0] - self.distances[4][1][0], self.distances[4][0][1] - self.distances[4][1][1])
        dist50_2 = math.hypot(self.distances[5][0][0] - self.distances[5][1][0], self.distances[5][0][1] - self.distances[5][1][1])
        '''
        dist10_1 = self.getPx(0)
        dist10_2 = self.getPx(1)
        dist50_1 = self.getPx(2)
        dist50_2 = self.getPx(3)
        dist90_1 = self.getPx(4)
        dist90_2 = self.getPx(5)

        result = (((dist10_1+dist10_2+dist90_1+dist90_2)/2) + (dist50_1+dist50_2))/2
        return result
    
    def getPx(self, index):
        return round(math.hypot(self.distances[index][0][0] - self.distances[index][1][0], self.distances[index][0][1] - self.distances[index][1][1]), 0)



class Knot:
    def __init__(self):
        self.coordinates= []
    
    def addPoint(self, x, y):
        self.coordinates.append([x, y])

class Cube:
    '''
    class definition for a cube
    https://www.w3schools.com/python/python_classes.asp
    '''

    class Cube_View:
        '''
        class to save the different views from different sides
        '''

        def __init__(self, side1=None, side2=None, side3=None, side4=None):
            '''
            1: Face, also Frontansicht des Block-Querschnittes,
            2: Oberseite,
            3: Rückseite, also gegenüberliegend von 1,
            4: Unterseite, also gegenüberliegend von 2.
            '''
            self.side = [side1, side2, side3, side4]
            self.side_id = ["1", "2", "3", "4"]
        
        def overwrite_side(self, side_id, image_path):
            self.side[side_id - Constants.ENUMARATION_OFFSET] = image_path


    def __init__(self, cube_x, cube_y, cube_path, cube_batch, ppi, reticulated):
        self.x = int(cube_x)
        self.y = int(cube_y)
        self.path = cube_path
        self.batch = cube_batch
        self.reticulated = reticulated
        self.ppi = ppi
        self.view = None
    
    def add_image_to_view(self, image_path, side_id):
        '''
        this OVERWRITES the image that is stored in the view-list
        '''
        #create view if for any reason it hasnt happened
        if self.view is None:
            self.view = self.Cube_View()
        #OVERWRITE image path
        self.view.overwrite_side(side_id, image_path)

    '''
    define how this class is printed
    https://stackoverflow.com/questions/1535327/how-to-print-instances-of-a-class-using-print
    '''
    #one method to produce the string
    def details(self):
        return "Cube: x=" + str(self.x) + " y=" + str(self.y)  + " batch=" + self.batch + " reticulated=" + str(self.reticulated) + " ppi=" + str(self.ppi)

    def name(self):
        return str(self.x) + "-" + str(self.y)

    #python methods
    def __repr__(self):
        return self.details()
    def __str__(self):
        return self.name()

class Foam_Label_Tool:

    def __init__(self):
        self.name = "cool label tool"

    def twoDigits(self, number):
        if (len(str(number)) < 2):
            return str("0" + str(number))
        else:
            return str(number)

    def writeResult(self, knots, center, measurement, cube, side_id):
        data = {}
        data['measurement'] = []
        data['measurement'].append({
            'knot1': str(knots[0].coordinates),
            'knot2': str(knots[1].coordinates),
            'bridge1' : str(center[0]),
            'bridge2' : str(center[1]),
            'measurement10_1' : str(measurement.distances[0]),
            'measurement10_2' : str(measurement.distances[1]),
            'measurement50_1' : str(measurement.distances[2]),
            'measurement50_2' : str(measurement.distances[3]),
            'measurement90_1' : str(measurement.distances[4]),
            'measurement90_2' : str(measurement.distances[5]),
            'px10' : str(measurement.getPx(0)+measurement.getPx(1)),
            'px50' : str(measurement.getPx(2)+measurement.getPx(3)),
            'px90' : str(measurement.getPx(4)+measurement.getPx(5)),
            'calculated_thickness' : str(measurement.getThickness())
        })
        json_name = cube.path + "/image_" + self.twoDigits(cube.x) + "_" + self.twoDigits(cube.y) + "_" + side_id + ".json"
        if os.path.isfile(json_name):
            with open(json_name) as outfile:
                old = json.load(outfile)
                temp = old['measurement']
                for item in temp:
                    data['measurement'].append(item)
        with open(json_name, 'w') as outfile:
            print("measurements in json: " + str(len(data['measurement'])))
            json.dump(data, outfile)
        
            


    def walklevel(self, some_dir, level=0):
        '''
        mod of os.walk to only get x levels deep https://stackoverflow.com/questions/229186/os-walk-without-digging-into-directories-below
        '''
        some_dir = some_dir.rstrip(os.path.sep)
        assert os.path.isdir(some_dir)
        num_sep = some_dir.count(os.path.sep)
        for root, dirs, files in os.walk(some_dir):
            yield root, dirs, files
            num_sep_this = root.count(os.path.sep)
            if num_sep + level <= num_sep_this:
                del dirs[:]

    def start(self):
        '''
        handle call arguments
        '''
        ap = argparse.ArgumentParser()
        ap.add_argument("-d", "--dataset", default="/home/jonaszagatta/gitprojects/datasets/foam/", help="path to input dataset (folder) with subfolders for all foam batches")
        ap.add_argument("-g", "--gamma", type=bool, default=False, help="do you want to use the gamma images?")
        
        # TODO: Delete
        ap.add_argument("-j", "--json", type=bool, default=False, help="Do you only want to debug the json saving?")
        
        args = vars(ap.parse_args())

        '''
        get all folders in dataset for selection
        based on https://www.tutorialspoint.com/python/os_walk.htm + walklevel
        initialize array and append: https://www.geeksforgeeks.org/python-which-is-faster-to-initialize-lists/
        '''
        foam_dir = []
        foam_name = []
        for root, dirs, files in self.walklevel(args["dataset"]):
            for name in dirs:
                foam_dir.append(os.path.join(root, name))
                foam_name.append(name)


        '''
        show menu to select batch 
        from https://stackoverflow.com/questions/45022566/create-python-cli-with-select-interface
        '''
        print("select the foam you want to label")
        terminal_menu = TerminalMenu(foam_name)
        choice_index = terminal_menu.show()
        print(foam_dir[choice_index])
        
        
        '''
        ppi and batch and reticulation are now fixed because of folder structure
        only works with the following strucutre
        PPI<ppi>_<reti>_<batch>
        PPI10_Reti_20-1802247-3
        '''
        name_splitstring = foam_name[choice_index].split(Constants.SEPARATOR)
        ppi = name_splitstring[0].strip(Constants.PPI_STRING)
        reticulated = False
        if Constants.RETICULATED_SIGNIFIER in name_splitstring[1]:
            reticulated = True
        batch = name_splitstring[2]


        #put all images in one list
        image_path = []
        image_name = []
        for root, dirs, files in self.walklevel(foam_dir[choice_index]):
            for name in files:
                if not Constants.JSON in name:
                    #only use non-gamma images for now
                    #TODO: implement gamma images
                    if not args["gamma"]:
                        if Constants.GAMMA not in name: 
                            #make lists of paths and filenames
                            image_path.append(os.path.join(root, name))
                            image_name.append(name)
                    else:
                        if Constants.GAMMA in name: 
                            #make lists of paths and filenames
                            image_path.append(os.path.join(root, name))
                            image_name.append(name)

        #make them alphabetically sorted
        image_name.sort()
        image_path.sort()

        cubes = []
        #put images in cubes
        # https://stackoverflow.com/questions/1663807/how-to-iterate-through-two-lists-in-parallel
        for [name, path] in zip(image_name, image_path):
            print("name: " + name)
            print("path: " + path)
            splitstring = name.split(Constants.SEPARATOR)
            x = int(splitstring[1])
            y = int(splitstring[2])
            side = int(splitstring[3])

            #check if cube exists
            found = False
            for cube in cubes:
                if cube.x is x:
                    if cube.y is y:
                        # cube exists -> break because we dont need to iterate the list anymore
                        found = True
                        break
            if not found:
                #cube doesnt exist
                #cube_x, cube_y, cube_path, cube_batch, ppi, reticulated):
                new_cube= Cube(x, y, foam_dir[choice_index], batch, ppi, reticulated)
                cubes.append(new_cube)
            #once we're here cube does definitely exists -> add side to it
            new_cube.add_image_to_view(path, side)
        
        '''
        give user cubes to select from
        '''
        cube_names = []
        for cube in cubes:
            cube_names.append(str(cube))
        cube_names.append("all")
        print("which cube do you want?")
        terminal_menu = TerminalMenu(cube_names)
        cube_choice_index = terminal_menu.show()

        cubes_selection = []
        if cube_choice_index > len(cubes) - 1:
            #selected "all"
            for cube in cubes:
                cubes_selection.append(cube)
        else:
            cubes_selection.append(cubes[cube_choice_index])

        print("you selected the following cubes for labeling")
        for selected in cubes_selection:
            print(selected.details())

        '''
        show pictures of selected cubes
        '''

        for cube in cubes_selection:
            for [image, side_id] in zip(cube.view.side, cube.view.side_id):

                # TODO: delete
                if args["json"]:
                    knots = [Knot(), Knot()]
                    center = []
                    measurement = Measurement()
                    # fake knots
                    # "knot1": "[[710, 769], [697, 805], [739, 801]]", "knot2": "[[777, 803], [804, 780], [798, 827]]"
                    knots[0].addPoint(710, 769)
                    knots[0].addPoint(697, 805)
                    knots[0].addPoint(739, 801)
                    knots[1].addPoint(777, 803)
                    knots[1].addPoint(804, 780)
                    knots[1].addPoint(798, 827)
                    # fake center
                    center1 = ((knots[0].coordinates[0][0]+knots[0].coordinates[1][0]+knots[0].coordinates[2][0])//3, (knots[0].coordinates[0][1]+knots[0].coordinates[1][1]+knots[0].coordinates[2][1])//3) 
                    center.append(center1)
                    center2 = ((knots[1].coordinates[0][0]+knots[1].coordinates[1][0]+knots[1].coordinates[2][0])//3, (knots[1].coordinates[0][1]+knots[1].coordinates[1][1]+knots[1].coordinates[2][1])//3) 
                    center.append(center2)
                    
                    # fake measurement
                    # "measurement10_1": "[(761, 792), (763, 814)]", "measurement10_2": "[(761, 792), (759, 775)]", "measurement50_1": "[(801, 791), (801, 807)]", "measurement50_2": "[(801, 791), (800, 775)]", "measurement90_1": "[(841, 789), (841, 808)]", "measurement90_2": "[(841, 789), (839, 757)]"
                    measurement.add_measurement((761, 792), (763, 814))
                    measurement.add_measurement((761, 792), (763, 814))
                    measurement.add_measurement((761, 792), (763, 814))
                    measurement.add_measurement((761, 792), (763, 814))
                    measurement.add_measurement((761, 792), (763, 814))
                    measurement.add_measurement((761, 792), (763, 814))
                    input("Press Enter to write result...")
                    self.writeResult(knots, center, measurement, cube, side_id)
                    input("Press Enter to continue to next cube...")
                    continue

                #https://www.life2coding.com/resize-opencv-window-according-screen-resolution/
                img = cv.imread(image)
            
                #define the screen resulation
                screen_res = Constants.IMG_HEIGHT, Constants.IMG_WIDTH
                scale_width = screen_res[0] / img.shape[1]
                scale_height = screen_res[1] / img.shape[0]
                scale = min(scale_width, scale_height)
            
                #resized window width and height
                window_width = int(img.shape[1] * scale)
                window_height = int(img.shape[0] * scale)
            
                title = cube.details() + " side: " + side_id
                #cv2.WINDOW_NORMAL makes the output window resizealbe
                cv.namedWindow(title, cv.WINDOW_NORMAL)
            
                #resize the window according to the screen resolution
                cv.resizeWindow(title, window_width, window_height)

                #detect mouse click https://stackoverflow.com/questions/28327020/opencv-detect-mouse-position-clicking-over-a-picture
                #hand another parameter to callback function: https://stackoverflow.com/questions/47114360/what-should-be-the-arguments-of-cv2-setmousecallback
                #cv.setMouseCallback(title, DrawOps.draw_line, [img, title])
                cv.imshow(title ,img)
                #detect if window is closed https://medium.com/@mh_yip/opencv-detect-whether-a-window-is-closed-or-close-by-press-x-button-ee51616f7088
                while cv.getWindowProperty(title, cv.WND_PROP_VISIBLE) >= 1:
                    k = cv.waitKey(20) & 0xFF
                    if k == 27:
                        cv.destroyAllWindows()
                        break
                    elif k == ord('k'):
                        print("drawing knots")
                        knots = [Knot(), Knot()]
                        center = []
                        cv.setMouseCallback(title, DrawOps.draw_knot, [title, img, knots, center])
                    elif k == ord('m'):
                        print("measuring thickness")
                        measurement = Measurement()
                        measurement_spots = []
                        #add 10%, 50% and 90% measurement spots
                        measurement_spots.append([int(center[0][0] - 0.1 * (center[0][0] - center[1][0])),int(center[0][1] - 0.1 * (center[0][1] - center[1][1]))])
                        measurement_spots.append([int(center[0][0] - 0.5 * (center[0][0] - center[1][0])),int(center[0][1] - 0.5 * (center[0][1] - center[1][1]))])
                        measurement_spots.append([int(center[0][0] - 0.9 * (center[0][0] - center[1][0])),int(center[0][1] - 0.9 * (center[0][1] - center[1][1]))])

                        #backup img
                        img_bk = copy.deepcopy(img)
                        cv.setMouseCallback(title, DrawOps.measurement, [title, img, measurement, center, measurement_spots, img_bk])
                    elif k == ord('s'):
                        #show and save
                        img = cv.imread(image)
                        DrawOps.show(img, title, measurement, knots, center)
                        #save
                        self.writeResult(knots, center, measurement, cube, side_id)
                    elif k == ord('n'):
                        cv.destroyAllWindows()
                        break


if __name__ == '__main__':
    labeltool = Foam_Label_Tool()
    labeltool.start()