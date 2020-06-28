import json
from json import JSONDecodeError
import cv2 as cv
import numpy as np
import argparse
from simple_term_menu import TerminalMenu
import os
from os import walk

class Constants:
    """Constants for this module."""
    SEPARATOR = "_"
    GAMMA = "gamma"
    ENUMARATION_OFFSET = 1
    PPI_STRING = "PPI"
    RETICULATED_SIGNIFIER = "Reti"
    SIDES = ["1", "2", "3", "4", "all"]


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
                #only use non-gamma images for now
                #TODO: implement gamma images
                if Constants.GAMMA not in name: 
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
                new_cube= Cube(x, y, path, batch, ppi, reticulated)
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



if __name__ == '__main__':
    labeltool = Foam_Label_Tool()
    labeltool.start()